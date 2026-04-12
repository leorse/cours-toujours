package fr.parcours.model.content;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
public class RoadStep {
    private String id;
    private String title;
    private String subtitle;
    private String type = "cours";
    private int order;
    private String subjectId;
    private String chapterId;
    private String contentFile;
    private Map<String, Object> selection;
    private String scope;
    private String strategy = "weakest_points";
    private boolean activated = false;
    private List<Map<String, Object>> pages = new ArrayList<>();
}
