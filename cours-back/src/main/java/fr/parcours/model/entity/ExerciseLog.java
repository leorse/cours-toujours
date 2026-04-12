package fr.parcours.model.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "exerciselog")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ExerciseLog {

    @Id
    @Column(name = "id", nullable = false)
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "tag")
    private String tag;

    @Column(name = "question_id")
    private String questionId;

    @Column(name = "is_correct")
    private boolean isCorrect;

    @Column(name = "timestamp")
    private LocalDateTime timestamp;

    @Column(name = "difficulty")
    @Builder.Default
    private int difficulty = 1;
}
