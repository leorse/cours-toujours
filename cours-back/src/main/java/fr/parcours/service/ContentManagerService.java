package fr.parcours.service;

import fr.parcours.model.content.*;
import fr.parcours.model.content.Character;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.yaml.snakeyaml.Yaml;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
@Slf4j
public class ContentManagerService {

    @Value("${parcours.content.path}")
    private String contentBasePath;

    // ── Caches en mémoire ────────────────────────────────────────────────────
    @Getter private final Map<String, Subject> subjects = new ConcurrentHashMap<>();
    @Getter private final Map<String, Chapter> chapters = new ConcurrentHashMap<>();
    @Getter private final Map<String, RoadStep> allSteps = new ConcurrentHashMap<>();
    @Getter private final Map<String, ExerciseTemplate> templates = new ConcurrentHashMap<>();
    @Getter private final Map<String, Event> events = new ConcurrentHashMap<>();
    @Getter private final Map<String, Character> characters = new ConcurrentHashMap<>();

    // ── Point d'entrée ───────────────────────────────────────────────────────
    public void loadAll() {
        subjects.clear();
        chapters.clear();
        allSteps.clear();
        templates.clear();
        events.clear();
        characters.clear();

        loadCharacters();
        loadCoursYaml();
    }

    // ── Chargement des personnages ────────────────────────────────────────────
    @SuppressWarnings("unchecked")
    private void loadCharacters() {
        Path charPath = resolve("config/personnages.yaml");
        if (!Files.exists(charPath)) return;
        try {
            Map<String, Object> raw = loadYaml(charPath);
            if (raw == null) return;
            Object persos = raw.get("personnages");
            if (persos instanceof List<?> list) {
                for (Object item : list) {
                    if (item instanceof Map<?, ?> m) {
                        Character c = mapToCharacter((Map<String, Object>) m);
                        characters.put(c.getId(), c);
                    }
                }
            }
        } catch (Exception e) {
            log.warn("Erreur chargement personnages: {}", e.getMessage());
        }
    }

    // ── Chargement du cours.yaml principal ───────────────────────────────────
    @SuppressWarnings("unchecked")
    private void loadCoursYaml() {
        Path coursPath = resolve("cours.yaml");
        if (!Files.exists(coursPath)) {
            log.error("cours.yaml introuvable à {}", coursPath);
            return;
        }
        Map<String, Object> raw = loadYaml(coursPath);
        if (raw == null) return;

        List<Object> cours = (List<Object>) raw.get("cours");
        if (cours == null) return;

        for (Object entry : cours) {
            if (!(entry instanceof Map<?, ?> m)) continue;
            Map<String, Object> item = (Map<String, Object>) m;

            // Événements globaux
            if (item.containsKey("events")) {
                Object evts = item.get("events");
                if (evts instanceof List<?> evtList) {
                    for (Object evt : evtList) {
                        if (evt instanceof Map<?, ?> em) {
                            Event event = mapToEvent((Map<String, Object>) em);
                            if (event.getId() != null) events.put(event.getId(), event);
                        }
                    }
                }
                continue;
            }

            // Pages de matières
            Object pageVal = item.get("page");
            String imageVal = (String) item.get("image");

            String routeFile;
            if (pageVal instanceof String s) {
                routeFile = s;
            } else if (pageVal instanceof Map<?, ?> pm) {
                Map<String, Object> pageMap = (Map<String, Object>) pm;
                routeFile = (String) pageMap.get("content");
                if (imageVal == null) imageVal = (String) pageMap.get("image");
            } else {
                continue;
            }
            if (routeFile == null) continue;
            loadSubject(routeFile, imageVal);
        }
    }

    // ── Chargement d'une matière ─────────────────────────────────────────────
    @SuppressWarnings("unchecked")
    private void loadSubject(String routeFile, String image) {
        Path routePath = resolve(routeFile);
        if (!Files.exists(routePath)) {
            log.warn("Fichier matière introuvable: {}", routePath);
            return;
        }
        Map<String, Object> raw = loadYaml(routePath);
        if (raw == null) return;

        String subjectDir = routeFile.contains("/") ? routeFile.substring(0, routeFile.lastIndexOf('/')) : "";
        String subjectId = subjectDir.isEmpty() ? Paths.get(routeFile).getFileName().toString().replace(".yaml", "") : subjectDir;

        Subject subject = new Subject();
        subject.setId(subjectId);
        subject.setName((String) raw.getOrDefault("title", subjectId));
        subject.setImage(image);
        subjects.put(subjectId, subject);

        // Charger les templates d'exercices de la matière
        loadTemplatesForSubject(subjectId, resolve(subjectDir));

        // Charger les étapes (avec ou sans chapitres)
        if (raw.containsKey("chapters")) {
            loadChapters(subjectId, subjectDir, (List<Object>) raw.get("chapters"));
        } else if (raw.containsKey("road")) {
            loadSteps(subjectId, null, (List<Object>) raw.get("road"), 0);
        }

        log.info("📌 Matière '{}': {} étapes", subjectId, allSteps.values().stream()
            .filter(s -> s.getSubjectId().equals(subjectId)).count());
    }

    // ── Chargement des chapitres ──────────────────────────────────────────────
    @SuppressWarnings("unchecked")
    private void loadChapters(String subjectId, String subjectDir, List<Object> chapList) {
        int globalIdx = 0;
        int chapOrder = 0;
        for (Object chapEntry : chapList) {
            if (!(chapEntry instanceof Map<?, ?> m)) continue;
            Map<String, Object> cm = (Map<String, Object>) m;

            Chapter chapter = new Chapter();
            chapter.setId(subjectId + "." + cm.get("id"));
            chapter.setTitle((String) cm.getOrDefault("title", ""));
            chapter.setSubjectId(subjectId);
            chapter.setOrder(chapOrder++);
            chapter.setIcon((String) cm.get("icon"));
            chapters.put(chapter.getId(), chapter);

            // Route inline ou fichier externe
            List<Object> roadEntries;
            Object roadVal = cm.get("road");
            if (roadVal instanceof String roadFile) {
                Path chapPath = resolve(subjectDir + "/" + roadFile);
                roadEntries = loadChapterFile(chapPath);
            } else if (roadVal instanceof List<?> inlineList) {
                roadEntries = (List<Object>) inlineList;
            } else {
                continue;
            }

            globalIdx = loadSteps(subjectId, chapter.getId(), roadEntries, globalIdx);
        }
    }

    // ── Chargement d'un fichier de chapitre externe ───────────────────────────
    @SuppressWarnings("unchecked")
    private List<Object> loadChapterFile(Path path) {
        if (!Files.exists(path)) {
            log.warn("Fichier chapitre introuvable: {}", path);
            return List.of();
        }
        Map<String, Object> raw = loadYaml(path);
        if (raw == null) return List.of();
        Object chapter = raw.get("chapter");
        if (chapter instanceof List<?> list) return (List<Object>) list;
        log.warn("Clé 'chapter' introuvable dans {}", path);
        return List.of();
    }

    // ── Chargement des étapes ─────────────────────────────────────────────────
    @SuppressWarnings("unchecked")
    private int loadSteps(String subjectId, String chapterId, List<Object> entries, int startIdx) {
        int idx = startIdx;
        for (Object entry : entries) {
            if (!(entry instanceof Map<?, ?> m)) continue;
            Map<String, Object> sm = (Map<String, Object>) m;
            String sType = (String) sm.getOrDefault("type", "cours");

            if ("sequence".equals(sType)) {
                // Expansion sequence: repeat -> N étapes identiques numérotées
                int repeat = (int) sm.getOrDefault("repeat", 1);
                String baseId = (String) sm.get("id");
                String titleTemplate = (String) sm.getOrDefault("title", baseId);
                Map<String, Object> stepConfig = (Map<String, Object>) sm.getOrDefault("step_config", Map.of());

                for (int i = 1; i <= repeat; i++) {
                    String rawId = baseId + "_" + i;
                    String stepId = subjectId + "." + rawId;
                    String title = titleTemplate.replace("{index}", String.valueOf(i));

                    RoadStep step = new RoadStep();
                    step.setId(stepId);
                    step.setTitle(title);
                    step.setType((String) stepConfig.getOrDefault("type", "practice"));
                    step.setOrder(idx++);
                    step.setSubjectId(subjectId);
                    step.setChapterId(chapterId);
                    step.setActivated((boolean) sm.getOrDefault("activated", false));

                    Object selRaw = stepConfig.get("selection");
                    if (selRaw instanceof Map<?, ?> selMap) {
                        // Remplacer {index} dans la sélection
                        Map<String, Object> sel = interpolateSelection((Map<String, Object>) selMap, i);
                        step.setSelection(sel);
                    }
                    step.setPages(toListOfMaps(stepConfig.get("pages")));
                    allSteps.put(stepId, step);
                }
            } else {
                String rawId = (String) sm.get("id");
                if (rawId == null) continue;
                String stepId = subjectId + "." + rawId;

                RoadStep step = new RoadStep();
                step.setId(stepId);
                step.setTitle((String) sm.getOrDefault("title", rawId));
                step.setSubtitle((String) sm.get("subtitle"));
                step.setType(sType);
                step.setOrder(idx++);
                step.setSubjectId(subjectId);
                step.setChapterId(chapterId);
                step.setContentFile((String) sm.get("content"));
                step.setScope((String) sm.get("scope"));
                step.setStrategy((String) sm.getOrDefault("strategy", "weakest_points"));
                step.setActivated((boolean) sm.getOrDefault("activated", false));

                Object selRaw = sm.get("selection");
                if (selRaw instanceof Map<?, ?> selMap) step.setSelection((Map<String, Object>) selMap);
                step.setPages(toListOfMaps(sm.get("pages")));
                allSteps.put(stepId, step);
            }
        }
        return idx;
    }

    // ── Chargement des templates d'exercices ──────────────────────────────────
    @SuppressWarnings("unchecked")
    private void loadTemplatesForSubject(String subjectId, Path subjectPath) {
        if (!Files.exists(subjectPath)) return;
        try {
            Files.walk(subjectPath)
                .filter(p -> p.toString().endsWith(".yaml"))
                .filter(p -> {
                    String name = p.getFileName().toString();
                    return !name.equals("meta.yaml") && !name.startsWith("route_")
                        && !name.startsWith("dialogue_") && !name.equals("tags.yaml");
                })
                .forEach(p -> loadTemplateFile(subjectId, p));
        } catch (IOException e) {
            log.warn("Erreur scan templates pour {}: {}", subjectId, e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    private void loadTemplateFile(String subjectId, Path path) {
        Map<String, Object> raw = loadYaml(path);
        if (raw == null) return;

        // Templates statiques
        Object tmplList = raw.get("templates");
        if (tmplList instanceof List<?> list) {
            for (Object item : list) {
                if (item instanceof Map<?, ?> m) {
                    ExerciseTemplate t = mapToTemplate((Map<String, Object>) m, subjectId);
                    if (t.getId() != null) templates.put(t.getId(), t);
                }
            }
        }

        // Générateurs
        Object genList = raw.get("generators");
        if (genList instanceof List<?> list) {
            for (Object item : list) {
                if (item instanceof Map<?, ?> m) {
                    ExerciseTemplate t = mapToGenerator((Map<String, Object>) m, subjectId);
                    if (t.getId() != null) templates.put(t.getId(), t);
                }
            }
        }
    }

    // ── Getters utilitaires ───────────────────────────────────────────────────

    public Optional<Subject> getSubject(String id) {
        return Optional.ofNullable(subjects.get(id));
    }

    public Optional<RoadStep> getStep(String id) {
        return Optional.ofNullable(allSteps.get(id));
    }

    public Optional<ExerciseTemplate> getTemplate(String id) {
        return Optional.ofNullable(templates.get(id));
    }

    public Optional<Event> getEvent(String id) {
        return Optional.ofNullable(events.get(id));
    }

    public Optional<Character> getCharacter(String id) {
        return Optional.ofNullable(characters.get(id));
    }

    public List<Chapter> getChaptersForSubject(String subjectId) {
        return chapters.values().stream()
            .filter(c -> c.getSubjectId().equals(subjectId))
            .sorted(Comparator.comparingInt(Chapter::getOrder))
            .collect(Collectors.toList());
    }

    public List<RoadStep> getStepsForChapter(String chapterId) {
        return allSteps.values().stream()
            .filter(s -> chapterId.equals(s.getChapterId()))
            .sorted(Comparator.comparingInt(RoadStep::getOrder))
            .collect(Collectors.toList());
    }

    public List<RoadStep> getStepsForSubject(String subjectId) {
        return allSteps.values().stream()
            .filter(s -> subjectId.equals(s.getSubjectId()))
            .sorted(Comparator.comparingInt(RoadStep::getOrder))
            .collect(Collectors.toList());
    }

    public List<ExerciseTemplate> selectTemplates(List<String> targetTags, int difficulty) {
        return templates.values().stream()
            .filter(t -> t.getDifficulty() == difficulty)
            .filter(t -> targetTags.isEmpty() || t.getTags().stream().anyMatch(targetTags::contains))
            .collect(Collectors.toList());
    }

    public Map<String, Object> getDialogue(String subjectId, String file) {
        // Cherche d'abord dans le dossier du sujet, puis à la racine du contenu
        List<Path> candidates = List.of(
            resolve(subjectId + "/" + file),
            resolve(file)
        );
        for (Path p : candidates) {
            if (Files.exists(p)) {
                Map<String, Object> raw = loadYaml(p);
                if (raw != null) return raw;
            }
        }
        log.warn("Dialogue introuvable: {} / {}", subjectId, file);
        return Map.of();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private Path resolve(String relativePath) {
        return Paths.get(contentBasePath).resolve(relativePath).normalize();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> loadYaml(Path path) {
        try (FileInputStream fis = new FileInputStream(path.toFile())) {
            Yaml yaml = new Yaml();
            return yaml.load(fis);
        } catch (IOException e) {
            log.error("Erreur lecture YAML {}: {}", path, e.getMessage());
            return null;
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> interpolateSelection(Map<String, Object> sel, int index) {
        Map<String, Object> result = new HashMap<>();
        for (var entry : sel.entrySet()) {
            Object val = entry.getValue();
            if (val instanceof String s) {
                result.put(entry.getKey(), s.replace("{index}", String.valueOf(index)));
            } else if (val instanceof List<?> list) {
                List<Object> newList = new ArrayList<>();
                for (Object item : list) {
                    if (item instanceof String s) {
                        newList.add(s.replace("{index}", String.valueOf(index)));
                    } else {
                        newList.add(item);
                    }
                }
                result.put(entry.getKey(), newList);
            } else {
                result.put(entry.getKey(), val);
            }
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> toListOfMaps(Object raw) {
        if (raw instanceof List<?> list) {
            return list.stream()
                .filter(i -> i instanceof Map<?, ?>)
                .map(i -> (Map<String, Object>) i)
                .collect(Collectors.toList());
        }
        return new ArrayList<>();
    }

    @SuppressWarnings("unchecked")
    private ExerciseTemplate mapToTemplate(Map<String, Object> m, String subjectId) {
        ExerciseTemplate t = new ExerciseTemplate();
        t.setId((String) m.get("id"));
        Object tagsRaw = m.get("tags");
        if (tagsRaw instanceof List<?> tagList) {
            t.setTags(tagList.stream().map(Object::toString).collect(Collectors.toList()));
        }
        t.setDifficulty((int) m.getOrDefault("difficulty", 1));
        t.setVars((Map<String, Object>) m.get("vars"));
        t.setContent((Map<String, Object>) m.get("content"));
        t.setLogic((String) m.get("logic"));
        t.setRenderType((String) m.get("render_type"));
        t.setInteraction((String) m.getOrDefault("interaction", "input"));
        t.setMultiple((boolean) m.getOrDefault("multiple", false));
        t.setType((String) m.get("type"));
        return t;
    }

    @SuppressWarnings("unchecked")
    private ExerciseTemplate mapToGenerator(Map<String, Object> m, String subjectId) {
        ExerciseTemplate t = new ExerciseTemplate();
        t.setId((String) m.get("id"));
        Object tagsRaw = m.get("tags");
        if (tagsRaw instanceof List<?> tagList) {
            t.setTags(tagList.stream().map(Object::toString).collect(Collectors.toList()));
        }
        t.setDifficulty((int) m.getOrDefault("difficulty", 1));
        t.setGeneratorType((String) m.get("type"));
        t.setWeight((int) m.getOrDefault("weight", 1));
        // Tout le reste comme config du générateur
        Map<String, Object> config = new HashMap<>(m);
        config.remove("id");
        config.remove("tags");
        config.remove("difficulty");
        config.remove("type");
        config.remove("weight");
        t.setGeneratorConfig(config);
        return t;
    }

    @SuppressWarnings("unchecked")
    private Event mapToEvent(Map<String, Object> m) {
        Event e = new Event();
        e.setId((String) m.get("id"));
        e.setType((String) m.get("type"));
        Object cond = m.get("conditions");
        if (cond instanceof String s) {
            e.setConditions(List.of(s));
        } else if (cond instanceof List<?> list) {
            e.setConditions(list.stream().map(Object::toString).collect(Collectors.toList()));
        }
        e.setContent((String) m.get("content"));
        return e;
    }

    @SuppressWarnings("unchecked")
    private Character mapToCharacter(Map<String, Object> m) {
        Character c = new Character();
        String name = (String) m.get("name");
        // YAML uses "name", not "id" — derive id from name if needed
        String id = (String) m.getOrDefault("id", name != null ? name.toLowerCase() : null);
        c.setId(id);
        c.setName(name);
        c.setSpritesheet((String) m.get("spritesheet"));
        // YAML uses "width"/"height", not "frame_width"/"frame_height"
        Object fw = m.getOrDefault("frame_width", m.get("width"));
        Object fh = m.getOrDefault("frame_height", m.get("height"));
        if (fw instanceof Integer i) c.setFrameWidth(i);
        if (fh instanceof Integer i) c.setFrameHeight(i);
        Object emoRaw = m.get("emotions");
        if (emoRaw instanceof Map<?, ?> emoMap) {
            // Map format: {emotionName: [x, y]}
            Map<String, int[]> emotions = new HashMap<>();
            for (var entry : emoMap.entrySet()) {
                if (entry.getValue() instanceof List<?> coords && coords.size() >= 2) {
                    emotions.put(entry.getKey().toString(),
                        new int[]{(int) coords.get(0), (int) coords.get(1)});
                }
            }
            c.setEmotions(emotions);
        } else if (emoRaw instanceof List<?> emoList) {
            // List format: [{name: "content", coords: [x, y]}, ...]
            Map<String, int[]> emotions = new HashMap<>();
            for (Object item : emoList) {
                if (item instanceof Map<?, ?> em) {
                    String emoName = (String) em.get("name");
                    Object coordsRaw = em.get("coords");
                    if (emoName != null && coordsRaw instanceof List<?> cl && cl.size() >= 2) {
                        emotions.put(emoName, new int[]{(int) cl.get(0), (int) cl.get(1)});
                    }
                }
            }
            c.setEmotions(emotions);
        }
        return c;
    }
}
