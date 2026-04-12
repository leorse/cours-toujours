package fr.parcours.controller;

import fr.parcours.model.dto.StepResult;
import fr.parcours.model.dto.SubmitRequest;
import fr.parcours.service.ContentManagerService;
import fr.parcours.service.ProgressService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/submit")
@RequiredArgsConstructor
public class SubmitController {

    private final ProgressService progressService;
    private final ContentManagerService contentManager;

    @PostMapping
    public ResponseEntity<StepResult> submit(@RequestBody SubmitRequest request, HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();

        return contentManager.getStep(request.getStepId()).map(step -> {
            StepResult result = ("cours".equals(step.getType()) || "theory".equals(step.getType()))
                ? progressService.completeTheoryStep(userId, step.getId())
                : progressService.evaluateExercises(userId, request);
            return ResponseEntity.ok(result);
        }).orElse(ResponseEntity.notFound().build());
    }
}
