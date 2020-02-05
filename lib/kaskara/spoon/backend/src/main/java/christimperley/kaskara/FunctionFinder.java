package christimperley.kaskara;

import java.util.ArrayList;
import java.util.List;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.visitor.filter.AbstractFilter;

/**
 * Provides an interface for finding all function definitions within a given project.
 */
public class FunctionFinder {
    private final Project project;

    public static FunctionFinder forProject(Project project) {
        return new FunctionFinder(project);
    }

    protected FunctionFinder(Project project) {
        this.project = project;
    }

    /**
     * Finds all function declarations within the associated project.
     * @return  A list of all functions within the associated project.
     */
    public List<Function> find() {
        var elements = this.project.getModel().getElements(new AbstractFilter<CtMethod>() {
            @Override
            public boolean matches(CtMethod element) {
                // function must have body
                if (element.getBody() == null) {
                    return false;
                }
                // function must appear in file
                return element.getPosition().isValidPosition();
            }
        });

        List<Function> functions = new ArrayList<>();
        for (var element : elements) {
            var function = Function.forSpoonMethod(element);
            functions.add(function);
        }
        return functions;
    }
}
