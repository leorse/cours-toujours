package fr.parcours.controller;

import fr.parcours.service.ContentManagerService;
import fr.parcours.service.ProgressService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final ContentManagerService contentManager;
    private final ProgressService progressService;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getDashboard(HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();

        var subjects = new ArrayList<>(contentManager.getSubjects().values());
        var xpMap = progressService.getSubjectXpMap(userId);
        var completed = progressService.getCompletedStepIds(userId);

        var dtos = subjects.stream().map(s -> {
            var steps = contentManager.getStepsForSubject(s.getId());
            long done = steps.stream().filter(st -> completed.contains(st.getId())).count();
            Map<String, Object> dto = new LinkedHashMap<>();
            dto.put("id", s.getId()); dto.put("name", s.getName()); dto.put("image", s.getImage() != null ? s.getImage() : "");
            dto.put("xp", xpMap.getOrDefault(s.getId(), 0));
            dto.put("totalSteps", steps.size()); dto.put("completedSteps", done);
            dto.put("progressPercent", steps.size() > 0 ? (int)(done * 100 / steps.size()) : 0);
            return dto;
        }).toList();

        return ResponseEntity.ok(Map.of("subjects", dtos));
    }
}
