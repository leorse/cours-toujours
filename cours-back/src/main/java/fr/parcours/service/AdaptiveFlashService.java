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
public class AdaptiveFlashService {

    private static final double WEAK_THRESHOLD = 0.80;
    private static final double WEAK_RATIO = 0.70;

    private final ExerciseLogRepository logRepo;
    private final ContentManagerService contentManager;
    private final ExerciseEngineService engine;

    public List<GeneratedExercise> generateFlashExercises(String userId, String subjectId, int count) {
        List<ExerciseTemplate> all = contentManager.getTemplates().values().stream()
            .filter(t -> t.getTags().stream().anyMatch(tag -> tag.startsWith(subjectId)))
            .collect(Collectors.toList());
        if (all.isEmpty()) return List.of();

        Map<String, Double> rates = computeRates(userId, subjectId);
        List<String> weak = rates.entrySet().stream()
            .filter(e -> e.getValue() < WEAK_THRESHOLD).map(Map.Entry::getKey).toList();

        List<GeneratedExercise> result = new ArrayList<>();
        int weakCount = (int) Math.round(count * WEAK_RATIO);

        if (!weak.isEmpty()) {
            List<ExerciseTemplate> weakT = all.stream()
                .filter(t -> t.getTags().stream().anyMatch(weak::contains)).toList();
            if (!weakT.isEmpty()) result.addAll(engine.generateExercises(weakT, weakCount));
        }

        int remaining = count - result.size();
        if (remaining > 0) result.addAll(engine.generateExercises(all, remaining));
        Collections.shuffle(result);
        return result.stream().limit(count).toList();
    }

    private Map<String, Double> computeRates(String userId, String subjectId) {
        var logs = logRepo.findByUserIdAndTagStartingWith(userId, subjectId);
        Map<String, List<Boolean>> byTag = new HashMap<>();
        logs.forEach(l -> byTag.computeIfAbsent(l.getTag(), k -> new ArrayList<>()).add(l.isCorrect()));
        Map<String, Double> rates = new HashMap<>();
        byTag.forEach((tag, results) -> {
            long ok = results.stream().filter(b -> b).count();
            rates.put(tag, (double) ok / results.size());
        });
        return rates;
    }
}
