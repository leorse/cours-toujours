package fr.parcours.model.content;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
public class ExerciseTemplate {
    private String id;
    private List<String> tags = new ArrayList<>();
    private int difficulty = 1;
    private Map<String, Object> vars;
    private Map<String, Object> content;
    private String logic;
    private String renderType;
    private String interaction = "input";
    private boolean multiple = false;
    private String type;
    private String generatorType;
    private Map<String, Object> generatorConfig;
    private int weight = 1;
}
