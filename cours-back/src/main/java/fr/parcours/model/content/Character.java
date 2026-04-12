package fr.parcours.model.content;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;

@Data
@NoArgsConstructor
public class Character {
    private String id;
    private String name;
    private String spritesheet;
    private Map<String, int[]> emotions;
    private int frameWidth = 379;
    private int frameHeight = 379;
}
