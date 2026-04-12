package fr.parcours.controller;

import fr.parcours.model.entity.UserEvent;
import fr.parcours.repository.UserEventRepository;
import fr.parcours.service.ContentManagerService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/events")
@RequiredArgsConstructor
public class EventController {

    private final ContentManagerService contentManager;
    private final UserEventRepository userEventRepo;

    @GetMapping("/{eventId}")
    public ResponseEntity<Map<String, Object>> getEvent(@PathVariable String eventId, HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();

        return contentManager.getEvent(eventId).map(event -> {
            boolean shouldShow = true;
            if (event.getConditions() != null && event.getConditions().contains("first_view")) {
                shouldShow = !userEventRepo.existsByUserIdAndEventId(userId, eventId);
            }
            if (shouldShow && !userEventRepo.existsByUserIdAndEventId(userId, eventId)) {
                userEventRepo.save(UserEvent.builder().id(UUID.randomUUID().toString())
                    .userId(userId).eventId(eventId).timestamp(LocalDateTime.now()).build());
            }

            var dialogue = "dialogue".equals(event.getType()) && event.getContent() != null
                ? contentManager.getDialogue("", event.getContent()) : Map.of();

            return ResponseEntity.ok(Map.of(
                "id", event.getId(),
                "type", event.getType() != null ? event.getType() : "",
                "shouldShow", shouldShow,
                "dialogue", dialogue,
                "characters", contentManager.getCharacters()
            ));
        }).orElse(ResponseEntity.notFound().build());
    }
}
