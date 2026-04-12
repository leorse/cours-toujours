package fr.parcours.model.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "user")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @Column(name = "id", nullable = false)
    private String id;

    @Column(name = "username", nullable = false, unique = true)
    private String username;

    @Column(name = "avatar")
    private String avatar;

    @Column(name = "total_xp")
    @Builder.Default
    private int totalXp = 0;

    public boolean isAdmin() {
        return username != null && username.contains("_ADMIN");
    }

    public String getInitials() {
        if (username == null || username.isEmpty()) return "?";
        return username.substring(0, Math.min(2, username.length())).toUpperCase();
    }
}
