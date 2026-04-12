package fr.parcours.repository;

import fr.parcours.model.entity.RoadStepProgress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface RoadStepProgressRepository extends JpaRepository<RoadStepProgress, String> {
    List<RoadStepProgress> findByUserId(String userId);
    List<RoadStepProgress> findByUserIdAndIsCompleted(String userId, boolean isCompleted);
    Optional<RoadStepProgress> findByUserIdAndStepId(String userId, String stepId);
    void deleteByUserId(String userId);
}
