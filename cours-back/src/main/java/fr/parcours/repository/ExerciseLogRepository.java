package fr.parcours.repository;

import fr.parcours.model.entity.ExerciseLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ExerciseLogRepository extends JpaRepository<ExerciseLog, String> {
    List<ExerciseLog> findByUserId(String userId);

    @Query("SELECT e FROM ExerciseLog e WHERE e.userId = :userId AND e.tag LIKE :tagPrefix%")
    List<ExerciseLog> findByUserIdAndTagStartingWith(String userId, String tagPrefix);

    void deleteByUserId(String userId);
}
