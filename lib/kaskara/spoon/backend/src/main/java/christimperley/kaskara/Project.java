package christimperley.kaskara;

import spoon.Launcher;
import spoon.reflect.CtModel;

/**
 * Maintains information about the program under analysis that is used by various classes.
 */
public class Project {
    private final CtModel model;

    /**
     * Constructs a description of a project whose source code is in a given directory.
     * @param sourceDirectory   The absolute path to the source code directory.
     * @return  A description of the project.
     */
    public static Project build(String sourceDirectory) {
        var launcher = new Launcher();
        launcher.getEnvironment().setAutoImports(true);
        launcher.addInputResource(sourceDirectory);
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
