package fr.parcours.model.content;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
public class Event {
    private String id;
    private String type;
    private List<String> conditions;
    private String content;
}
