package fr.parcours.controller;

import fr.parcours.model.entity.RoadStepProgress;
import fr.parcours.repository.*;
import fr.parcours.service.ContentManagerService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

    private final RoadStepProgressRepository stepRepo;
    private final SubjectProgressRepository subjectRepo;
    private final ExerciseLogRepository logRepo;
    private final UserEventRepository eventRepo;
    private final UserRepository userRepo;
    private final ContentManagerService contentManager;

    private boolean isAdmin(HttpSession session) {
        String uid = (String) session.getAttribute("userId");
        return uid != null && userRepo.findById(uid).map(u -> u.isAdmin()).orElse(false);
    }

    @PostMapping("/reset")
    public ResponseEntity<Void> reset(HttpSession session) {
        if (!isAdmin(session)) return ResponseEntity.status(403).build();
        String uid = (String) session.getAttribute("userId");
        stepRepo.deleteByUserId(uid);
        subjectRepo.findByUserId(uid).forEach(subjectRepo::delete);
        logRepo.deleteByUserId(uid);
        eventRepo.findAll().stream().filter(e -> e.getUserId().equals(uid)).forEach(eventRepo::delete);
        userRepo.findById(uid).ifPresent(u -> { u.setTotalXp(0); userRepo.save(u); });
        return ResponseEntity.ok().build();
    }

    @PostMapping("/validate-all")
    public ResponseEntity<Void> validateAll(HttpSession session) {
        if (!isAdmin(session)) return ResponseEntity.status(403).build();
        String uid = (String) session.getAttribute("userId");
        contentManager.getAllSteps().values().forEach(step -> {
            var p = stepRepo.findByUserIdAndStepId(uid, step.getId())
                .orElse(RoadStepProgress.builder().id(UUID.randomUUID().toString()).userId(uid).stepId(step.getId()).build());
            p.setCompleted(true); p.setMastery(3); stepRepo.save(p);
        });
        return ResponseEntity.ok().build();
    }

    @PostMapping("/validate-step/{stepId}")
    public ResponseEntity<Void> validateStep(@PathVariable String stepId, HttpSession session) {
        if (!isAdmin(session)) return ResponseEntity.status(403).build();
        String uid = (String) session.getAttribute("userId");
        var p = stepRepo.findByUserIdAndStepId(uid, stepId)
            .orElse(RoadStepProgress.builder().id(UUID.randomUUID().toString()).userId(uid).stepId(stepId).build());
        p.setCompleted(true); p.setMastery(3); stepRepo.save(p);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/invalidate-step/{stepId}")
    public ResponseEntity<Void> invalidateStep(@PathVariable String stepId, HttpSession session) {
        if (!isAdmin(session)) return ResponseEntity.status(403).build();
        String uid = (String) session.getAttribute("userId");
        stepRepo.findByUserIdAndStepId(uid, stepId).ifPresent(p -> {
            p.setCompleted(false); p.setMastery(0); stepRepo.save(p);
        });
        return ResponseEntity.ok().build();
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> stats(HttpSession session) {
        if (!isAdmin(session)) return ResponseEntity.status(403).build();
        return ResponseEntity.ok(Map.of(
            "totalUsers", userRepo.count(),
            "totalSteps", contentManager.getAllSteps().size(),
            "totalTemplates", contentManager.getTemplates().size(),
            "subjects", contentManager.getSubjects().keySet()
        ));
    }

    @PostMapping("/reload-content")
    public ResponseEntity<Void> reloadContent(HttpSession session) {
        if (!isAdmin(session)) return ResponseEntity.status(403).build();
        contentManager.loadAll();
        return ResponseEntity.ok().build();
    }
}
