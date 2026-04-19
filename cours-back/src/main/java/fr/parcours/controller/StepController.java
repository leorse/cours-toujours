package fr.parcours.controller;

import fr.parcours.model.content.RoadStep;
import fr.parcours.model.dto.GeneratedExercise;
import fr.parcours.service.*;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.commonmark.ext.gfm.tables.TablesExtension;
import org.commonmark.parser.Parser;
import org.commonmark.renderer.html.HtmlRenderer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/api/steps")
@RequiredArgsConstructor
@Slf4j
public class StepController {

    private final ContentManagerService contentManager;
    private final ExerciseEngineService exerciseEngine;
    private final AdaptiveFlashService flashService;
    private final ReinforcementEngineService reinforcementEngine;

    @Value("${parcours.content.path}")
    private String contentPath;

    @GetMapping("/{stepId}")
    public ResponseEntity<Map<String, Object>> getStep(
            @PathVariable String stepId,
            @RequestParam(defaultValue = "0") int pageIdx,
            HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();

        return contentManager.getStep(stepId).map(step -> {
            Map<String, Object> result = buildResponse(step, pageIdx, userId);
            return ResponseEntity.ok(result);
        }).orElse(ResponseEntity.notFound().build());
    }

    private Map<String, Object> buildResponse(RoadStep step, int pageIdx, String userId) {
        var result = new LinkedHashMap<String, Object>();
        result.put("id", step.getId()); result.put("title", step.getTitle());
        result.put("type", step.getType()); result.put("subjectId", step.getSubjectId());
        result.put("chapterId", step.getChapterId());
        int totalPages = step.getPages().isEmpty() ? 1 : step.getPages().size();
        result.put("totalPages", totalPages); result.put("currentPage", pageIdx);
        result.put("isLastPage", pageIdx >= totalPages - 1);

        if (!step.getPages().isEmpty() && pageIdx < step.getPages().size()) {
            Map<String, Object> page = step.getPages().get(pageIdx);
            String pt = (String) page.getOrDefault("type", step.getType());
            result.put("pageType", pt);
            result.putAll(buildPagePayload(step, page, pt, userId));
        } else {
            result.put("pageType", step.getType());
            result.putAll(buildDirectPayload(step, userId));
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> buildPagePayload(RoadStep step, Map<String, Object> page, String pt, String userId) {
        var payload = new LinkedHashMap<String, Object>();
        switch (pt) {
            case "dialogue" -> {
                String f = (String) page.get("content");
                if (f != null) {
                    Map<String, Object> raw = contentManager.getDialogue(step.getSubjectId(), f);
                    payload.put("dialogue", normalizeDialogue(raw));
                    payload.put("characters", contentManager.getCharacters());
                }
                payload.put("conditions", page.get("conditions"));
            }
            case "cours", "theory" -> {
                String f = (String) page.getOrDefault("content", step.getContentFile());
                var rendered = renderMarkdownWithExercises(step.getSubjectId(), f);
                payload.put("markdownHtml", rendered.get("html"));
                if (!((List<?>) rendered.get("exercises")).isEmpty()) {
                    payload.put("inlineExercises", rendered.get("exercises"));
                }
            }
            default -> payload.putAll(buildDirectPayload(step, userId));
        }
        return payload;
    }

    private Map<String, Object> buildDirectPayload(RoadStep step, String userId) {
        var payload = new LinkedHashMap<String, Object>();
        switch (step.getType()) {
            case "cours", "theory" -> {
                var rendered = renderMarkdownWithExercises(step.getSubjectId(), step.getContentFile());
                payload.put("markdownHtml", rendered.get("html"));
                if (!((List<?>) rendered.get("exercises")).isEmpty()) {
                    payload.put("inlineExercises", rendered.get("exercises"));
                }
            }
            case "practice", "exam", "validation" -> payload.put("exercises", generateForStep(step));
            case "reinforcement" -> payload.put("exercises", reinforcementEngine.generateReinforcementExercises(userId, step.getScope(), 10));
            case "flash" -> payload.put("exercises", flashService.generateFlashExercises(userId, step.getSubjectId(), 10));
        }
        return payload;
    }

    @SuppressWarnings("unchecked")
    private List<GeneratedExercise> generateForStep(RoadStep step) {
        if (step.getSelection() == null) return List.of();
        List<String> targets = (List<String>) step.getSelection().getOrDefault("target", List.of());
        int count = toInt(step.getSelection().getOrDefault("count", 10));
        int diff = toInt(step.getSelection().getOrDefault("difficulty", 1));
        var templates = contentManager.selectTemplates(targets, diff);
        return exerciseEngine.generateExercises(templates, count);
    }

    private static final Pattern EXO_PLACEHOLDER = Pattern.compile("&&([\\w.]+)&&");

    /** Renders markdown to HTML and extracts &&templateId&& inline exercises. */
    private Map<String, Object> renderMarkdownWithExercises(String subjectId, String file) {
        if (file == null) return Map.of("html", "", "exercises", List.of());
        try {
            var path = Paths.get(contentPath, subjectId, file).normalize();
            if (!Files.exists(path)) path = Paths.get(contentPath, file).normalize();
            if (!Files.exists(path)) return Map.of("html", "", "exercises", List.of());
            String md = Files.readString(path);

            // Extract and replace &&templateId&& placeholders
            List<GeneratedExercise> exercises = new ArrayList<>();
            Matcher m = EXO_PLACEHOLDER.matcher(md);
            StringBuffer sb = new StringBuffer();
            while (m.find()) {
                String templateId = m.group(1);
                contentManager.getTemplate(templateId).ifPresent(tmpl ->
                    exerciseEngine.generateExercise(tmpl).ifPresent(exercises::add));
                // Replace with an empty marker (exercise rendered separately below the text)
                m.appendReplacement(sb, "");
            }
            m.appendTail(sb);

            var extensions = List.of(TablesExtension.create());
            var doc = Parser.builder().extensions(extensions).build().parse(sb.toString());
            String html = HtmlRenderer.builder().extensions(extensions).build().render(doc);
            return Map.of("html", html, "exercises", exercises);
        } catch (Exception e) {
            log.warn("Erreur lecture markdown {}/{}: {}", subjectId, file, e.getMessage());
            return Map.of("html", "", "exercises", List.of());
        }
    }

    /** Normalises raw dialogue YAML into a flat list of {character?, emotion?, page, image?} maps. */
    @SuppressWarnings("unchecked")
    private Map<String, Object> normalizeDialogue(Map<String, Object> raw) {
        Object dialogueList = raw.get("dialogue");
        if (!(dialogueList instanceof List<?> list)) return raw;

        String type = "monologue";
        List<Object> messages = null;

        for (Object item : list) {
            if (!(item instanceof Map<?, ?> entry)) continue;
            Map<String, Object> map = (Map<String, Object>) entry;
            if (map.containsKey("type")) type = (String) map.get("type");
            if (map.containsKey("message")) messages = (List<Object>) map.get("message");
        }

        if (messages == null) return raw;

        List<Map<String, Object>> normalized = new ArrayList<>();
        for (Object msg : messages) {
            if (!(msg instanceof Map<?, ?> rawMsg)) continue;
            Map<String, Object> msgMap = (Map<String, Object>) rawMsg;
            Map<String, Object> entry = new LinkedHashMap<>();

            if ("monologue".equals(type)) {
                // {page: "text", image: "file.png"}
                entry.put("page", msgMap.get("page"));
                if (msgMap.get("image") != null) entry.put("image", msgMap.get("image"));
            } else {
                // {CharacterName: "text", emotion: "emotion"}
                String emotion = (String) msgMap.get("emotion");
                for (var e : msgMap.entrySet()) {
                    if (!e.getKey().equals("emotion") && e.getValue() instanceof String text) {
                        entry.put("character", e.getKey().toLowerCase());
                        entry.put("page", text);
                        break;
                    }
                }
                if (emotion != null) entry.put("emotion", emotion);
            }
            normalized.add(entry);
        }

        return Map.of("dialogue", normalized, "type", type);
    }

    private int toInt(Object v) {
        if (v instanceof Integer i) return i;
        if (v instanceof Long l) return l.intValue();
        try { return Integer.parseInt(v.toString()); } catch (Exception e) { return 0; }
    }
}
