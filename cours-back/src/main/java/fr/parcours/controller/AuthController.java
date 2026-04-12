package fr.parcours.controller;

import fr.parcours.model.dto.UserDto;
import fr.parcours.model.entity.User;
import fr.parcours.repository.UserRepository;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final UserRepository userRepo;

    @GetMapping("/users")
    public List<UserDto> listUsers() {
        return userRepo.findAll().stream().map(this::toDto).toList();
    }

    @PostMapping("/login")
    public ResponseEntity<UserDto> login(@RequestBody Map<String, String> body, HttpSession session) {
        return userRepo.findById(body.get("userId"))
            .map(u -> { session.setAttribute("userId", u.getId()); return ResponseEntity.ok(toDto(u)); })
            .orElse(ResponseEntity.status(404).build());
    }

    @PostMapping("/users")
    public ResponseEntity<UserDto> createUser(@RequestBody Map<String, String> body, HttpSession session) {
        String username = body.get("username");
        if (username == null || username.isBlank()) return ResponseEntity.badRequest().build();
        if (userRepo.existsByUsername(username)) return ResponseEntity.status(409).build();
        User user = User.builder().id(UUID.randomUUID().toString())
            .username(username).avatar(body.getOrDefault("avatar", "")).totalXp(0).build();
        userRepo.save(user);
        session.setAttribute("userId", user.getId());
        return ResponseEntity.ok(toDto(user));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(HttpSession session) {
        session.invalidate();
        return ResponseEntity.ok().build();
    }

    @GetMapping("/me")
    public ResponseEntity<UserDto> me(HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        if (userId == null) return ResponseEntity.status(401).build();
        return userRepo.findById(userId).map(u -> ResponseEntity.ok(toDto(u)))
            .orElse(ResponseEntity.status(401).build());
    }

    private UserDto toDto(User u) {
        UserDto dto = new UserDto();
        dto.setId(u.getId()); dto.setUsername(u.getUsername()); dto.setAvatar(u.getAvatar());
        dto.setTotalXp(u.getTotalXp()); dto.setAdmin(u.isAdmin()); dto.setInitials(u.getInitials());
        return dto;
    }
}
