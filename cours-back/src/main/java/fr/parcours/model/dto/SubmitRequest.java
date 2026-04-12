package fr.parcours.model.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
public class SubmitRequest {
    private String stepId;
    private Map<String, Object> answers;
    private List<GeneratedExercise> generatedExercises;
}
