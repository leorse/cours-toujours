package fr.parcours.model.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class UserDto {
    private String id;
    private String username;
    private String avatar;
    private int totalXp;
    private boolean isAdmin;
    private String initials;
}
