package fr.parcours.service;

import fr.parcours.model.dto.GeneratedExercise;
import fr.parcours.model.dto.StepResult;
import fr.parcours.model.dto.SubmitRequest;
import fr.parcours.model.entity.*;
import fr.parcours.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class ProgressService {

    private static final int XP_PER_CORRECT = 10;
    private static final int XP_THEORY = 20;
    private static final double PASS_THRESHOLD = 0.5;

    private final RoadStepProgressRepository stepRepo;
    private final SubjectProgressRepository subjectRepo;
    private final ExerciseLogRepository logRepo;
    private final UserRepository userRepo;
    private final SmartCompareService smartCompare;
    private final ContentManagerService contentManager;

    @Transactional
    public StepResult completeTheoryStep(String userId, String stepId) {
        var step = contentManager.getStep(stepId).orElseThrow();
        var p = stepRepo.findByUserIdAndStepId(userId, stepId)
            .orElse(RoadStepProgress.builder().id(UUID.randomUUID().toString()).userId(userId).stepId(stepId).build());
        p.setCompleted(true);
        stepRepo.save(p);
        addXp(userId, step.getSubjectId(), XP_THEORY);
        StepResult r = new StepResult();
        r.setSuccess(true);
        r.setXpEarned(XP_THEORY);
        r.setMessage("Cours terminé !");
        return r;
    }

    @Transactional
    public StepResult evaluateExercises(String userId, SubmitRequest request) {
        var step = contentManager.getStep(request.getStepId()).orElseThrow();
        List<GeneratedExercise> exercises = request.getGeneratedExercises() != null
            ? request.getGeneratedExercises() : List.of();
        Map<String, Object> answers = request.getAnswers() != null ? request.getAnswers() : Map.of();

        Map<String, Boolean> results = new LinkedHashMap<>();
        int correct = 0;
        for (GeneratedExercise ex : exercises) {
            boolean ok = smartCompare.compare(answers.get(ex.getId()), ex.getAnswer());
            results.put(ex.getId(), ok);
            if (ok) correct++;
            logExercise(userId, ex, ok);
        }

        int total = exercises.size();
        double score = total > 0 ? (double) correct / total : 0;
        boolean success = score >= PASS_THRESHOLD;
        int xp = correct * XP_PER_CORRECT;

        // Progression étape
        var p = stepRepo.findByUserIdAndStepId(userId, request.getStepId())
            .orElse(RoadStepProgress.builder().id(UUID.randomUUID().toString())
                .userId(userId).stepId(request.getStepId()).build());
        if (success) p.setCompleted(true);
        if ("validation".equals(step.getType())) {
            boolean perfect = score >= 1.0;
            p.setMastery(perfect ? Math.min(3, p.getMastery() + 1) : Math.max(0, p.getMastery() - 1));
        }
        stepRepo.save(p);
        if (success) addXp(userId, step.getSubjectId(), xp);

        StepResult r = new StepResult();
        r.setSuccess(success);
        r.setCorrectCount(correct);
        r.setTotalCount(total);
        r.setScorePercent(score * 100);
        r.setXpEarned(success ? xp : 0);
        r.setAnswerResults(results);
        r.setMessage(success ? "Bravo ! " + correct + "/" + total : "Essaie encore ! " + correct + "/" + total);
        return r;
    }

    public List<String> getCompletedStepIds(String userId) {
        return stepRepo.findByUserIdAndIsCompleted(userId, true)
            .stream().map(RoadStepProgress::getStepId).toList();
    }

    public Map<String, Integer> getMasteryMap(String userId) {
        Map<String, Integer> map = new HashMap<>();
        stepRepo.findByUserId(userId).forEach(p -> map.put(p.getStepId(), p.getMastery()));
        return map;
    }

    public Map<String, Integer> getSubjectXpMap(String userId) {
        Map<String, Integer> map = new HashMap<>();
        subjectRepo.findByUserId(userId).forEach(p -> map.put(p.getSubjectId(), p.getScore()));
        return map;
    }

    private void logExercise(String userId, GeneratedExercise ex, boolean ok) {
        if (ex.getTags() == null) return;
        for (String tag : ex.getTags()) {
            logRepo.save(ExerciseLog.builder()
                .id(UUID.randomUUID().toString())
                .userId(userId).tag(tag).questionId(ex.getId())
                .isCorrect(ok).timestamp(LocalDateTime.now()).difficulty(1)
                .build());
        }
    }

    private void addXp(String userId, String subjectId, int amount) {
        userRepo.findById(userId).ifPresent(u -> { u.setTotalXp(u.getTotalXp() + amount); userRepo.save(u); });
        var sp = subjectRepo.findByUserIdAndSubjectId(userId, subjectId)
            .orElse(SubjectProgress.builder().id(UUID.randomUUID().toString())
                .userId(userId).subjectId(subjectId).score(0).build());
        sp.setScore(sp.getScore() + amount);
        subjectRepo.save(sp);
    }
}
