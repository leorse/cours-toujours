package fr.parcours.model.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "roadstepprogress")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RoadStepProgress {

    @Id
    @Column(name = "id", nullable = false)
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "step_id", nullable = false)
    private String stepId;

    @Column(name = "is_completed")
    @Builder.Default
    private boolean isCompleted = false;

    @Column(name = "mastery")
    @Builder.Default
    private int mastery = 0;

    @Column(name = "answers", columnDefinition = "TEXT")
    private String answers;
}
