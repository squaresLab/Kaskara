package christimperley.kaskara;

import java.util.ArrayList;
import java.util.List;
import spoon.reflect.code.CtLoop;
import spoon.reflect.visitor.filter.AbstractFilter;

/**
 * Provides an interface for finding all loops within a given project.
 */
public class LoopFinder {
    private final Project project;

    public static LoopFinder forProject(Project project) {
        return new LoopFinder(project);
    }

    protected LoopFinder(Project project) {
        this.project = project;
    }

    /**
     * Finds all loops within the associated project.
     * @return  A list of all loops within the associated project.
     */
    public List<Loop> find() {
        var elements = this.project.getModel().getElements(new AbstractFilter<CtLoop>() {
            @Override
            public boolean matches(CtLoop element) {
                // loop must have body
                if (element.getBody() == null) {
                    return false;
                }
                // loop must appear in file
                return element.getPosition().isValidPosition();
            }
        });

        List<Loop> loops = new ArrayList<>();
        for (var element : elements) {
            loops.add(Loop.forSpoonLoop(element));
        }
        return loops;
    }
}
