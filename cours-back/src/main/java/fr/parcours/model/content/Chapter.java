package fr.parcours.model.content;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class Chapter {
    private String id;
    private String title;
    private String subjectId;
    private int order;
    private String icon;
}
