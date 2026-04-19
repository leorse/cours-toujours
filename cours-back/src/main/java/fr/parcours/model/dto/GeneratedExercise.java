package fr.parcours.model.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
public class GeneratedExercise {
    private String id;
    private String templateId;
    private String type;
    private String renderType;
    private boolean multiple;
    private String question;
    private List<String> options;
    private Object answer;
    private String explanation;
    private String unit;
    private Map<String, Object> variables;
    private List<String> tags;
    private Map<String, Object> meta;
    /** Tout le contenu YAML interpolé — les widgets custom lisent leurs paramètres ici */
    private Map<String, Object> data;
}
