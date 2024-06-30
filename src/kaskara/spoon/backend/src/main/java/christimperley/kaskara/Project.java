package christimperley.kaskara;

import java.util.List;
import spoon.Launcher;
import spoon.reflect.CtModel;

/**
 * Maintains information about the program under analysis that is used by various classes.
 */
public class Project {
    private final CtModel model;

    /**
     * Constructs a description of a Java project.
     * @param paths A list of paths to the source files or directories that should be indexed.
     * @return  A description of the project.
     */
    public static Project build(List<String> paths) {
        var launcher = new Launcher();
        launcher.getEnvironment().setAutoImports(true);
        for (var path : paths) {
            launcher.addInputResource(path);
        }
        var model = launcher.buildModel();
        return new Project(model);
    }

    protected Project(CtModel model) {
        this.model = model;
    }

    public final CtModel getModel() {
        return this.model;
    }
}
