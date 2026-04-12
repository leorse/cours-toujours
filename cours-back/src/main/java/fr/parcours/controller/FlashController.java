package fr.parcours.controller;

import fr.parcours.model.dto.StepResult;
import fr.parcours.model.dto.SubmitRequest;
import fr.parcours.service.AdaptiveFlashService;
import fr.parcours.service.ProgressService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/flash")
@RequiredArgsConstructor
public class FlashController {

    private final AdaptiveFlashService flashService;
    private final ProgressService progressService;

    @GetMapping("/{subjectId}")
    public ResponseEntity<Map<String, Object>> getFlash(
            @PathVariable String subjectId,
            @RequestParam(defaultValue = "10") int count,
            HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();
        var exercises = flashService.generateFlashExercises(userId, subjectId, count);
        return ResponseEntity.ok(Map.of("subjectId", subjectId, "exercises", exercises, "count", exercises.size()));
    }

    @PostMapping("/{subjectId}/submit")
    public ResponseEntity<StepResult> submitFlash(
            @PathVariable String subjectId,
            @RequestBody SubmitRequest request,
            HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();
        return ResponseEntity.ok(progressService.evaluateExercises(userId, request));
    }
}
