package fr.parcours.service;

import fr.parcours.model.content.ExerciseTemplate;
import fr.parcours.model.dto.GeneratedExercise;
import fr.parcours.repository.ExerciseLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ReinforcementEngineService {

    private final ExerciseLogRepository logRepo;
    private final ContentManagerService contentManager;
    private final ExerciseEngineService engine;

    public List<GeneratedExercise> generateReinforcementExercises(String userId, String scopeTag, int count) {
        List<ExerciseTemplate> scoped = contentManager.getTemplates().values().stream()
            .filter(t -> t.getTags().stream().anyMatch(tag -> tag.contains(scopeTag)))
            .collect(Collectors.toList());
        if (scoped.isEmpty()) return List.of();

        var logs = logRepo.findByUserIdAndTagStartingWith(userId, scopeTag);
        Map<String, List<Boolean>> byTag = new HashMap<>();
        logs.forEach(l -> byTag.computeIfAbsent(l.getTag(), k -> new ArrayList<>()).add(l.isCorrect()));
        Set<String> weak = byTag.entrySet().stream()
            .filter(e -> { long ok = e.getValue().stream().filter(b -> b).count();
                return (double) ok / e.getValue().size() < 0.80; })
            .map(Map.Entry::getKey).collect(Collectors.toSet());

        List<GeneratedExercise> result = new ArrayList<>();
        int weakCount = (int) Math.round(count * 0.60);
        int easyCount = (int) Math.round(count * 0.20);

        if (!weak.isEmpty()) {
            List<ExerciseTemplate> weakT = scoped.stream()
                .filter(t -> t.getTags().stream().anyMatch(weak::contains)).toList();
            if (!weakT.isEmpty()) result.addAll(engine.generateExercises(weakT, weakCount));
        }

        List<ExerciseTemplate> easy = scoped.stream().filter(t -> t.getDifficulty() == 1).toList();
        if (!easy.isEmpty()) result.addAll(engine.generateExercises(easy, easyCount));

        result.addAll(engine.generateExercises(scoped, count - result.size()));
        Collections.shuffle(result);
        return result.stream().limit(count).toList();
    }
}
