package fr.parcours.controller;

import fr.parcours.service.ContentManagerService;
import fr.parcours.service.ProgressService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/subjects")
@RequiredArgsConstructor
public class SubjectController {

    private final ContentManagerService contentManager;
    private final ProgressService progressService;

    @GetMapping("/{subjectId}")
    public ResponseEntity<Map<String, Object>> getSubject(@PathVariable String subjectId, HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();

        return contentManager.getSubject(subjectId).map(subject -> {
            var chapters = contentManager.getChaptersForSubject(subjectId);
            var completed = progressService.getCompletedStepIds(userId);

            var chapDtos = chapters.stream().map(c -> {
                var steps = contentManager.getStepsForChapter(c.getId());
                long done = steps.stream().filter(s -> completed.contains(s.getId())).count();
                Map<String, Object> dto = new LinkedHashMap<>();
                dto.put("id", c.getId()); dto.put("title", c.getTitle()); dto.put("icon", c.getIcon());
                dto.put("order", c.getOrder()); dto.put("totalSteps", steps.size()); dto.put("completedSteps", done);
                return dto;
            }).toList();

            Map<String, Object> result = new LinkedHashMap<>();
            result.put("subject", Map.of("id", subject.getId(), "name", subject.getName(), "image", subject.getImage() != null ? subject.getImage() : ""));
            result.put("chapters", chapDtos);
            return ResponseEntity.ok(result);
        }).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{subjectId}/chapters/{chapterId}")
    public ResponseEntity<Map<String, Object>> getChapter(
            @PathVariable String subjectId, @PathVariable String chapterId, HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();

        return contentManager.getSubject(subjectId).map(subject -> {
            // chapterId peut être le suffixe ou l'ID complet
            String fullChapterId = chapterId.contains(".") ? chapterId : subjectId + "." + chapterId;
            var steps = contentManager.getStepsForChapter(fullChapterId);
            var completed = progressService.getCompletedStepIds(userId);
            var mastery = progressService.getMasteryMap(userId);

            var stepDtos = steps.stream().map(s -> {
                Map<String, Object> dto = new LinkedHashMap<>();
                dto.put("id", s.getId()); dto.put("title", s.getTitle()); dto.put("subtitle", s.getSubtitle());
                dto.put("type", s.getType()); dto.put("order", s.getOrder()); dto.put("activated", s.isActivated());
                dto.put("completed", completed.contains(s.getId()));
                dto.put("mastery", mastery.getOrDefault(s.getId(), 0));
                return dto;
            }).toList();

            Map<String, Object> result = new LinkedHashMap<>();
            result.put("subject", Map.of("id", subject.getId(), "name", subject.getName()));
            result.put("chapterId", chapterId); result.put("steps", stepDtos);
            return ResponseEntity.ok(result);
        }).orElse(ResponseEntity.notFound().build());
    }
}
