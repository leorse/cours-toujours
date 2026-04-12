package fr.parcours.model.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;

@Data
@NoArgsConstructor
public class StepResult {
    private boolean success;
    private int xpEarned;
    private int correctCount;
    private int totalCount;
    private double scorePercent;
    private Map<String, Boolean> answerResults;
    private String nextUrl;
    private String message;
}
