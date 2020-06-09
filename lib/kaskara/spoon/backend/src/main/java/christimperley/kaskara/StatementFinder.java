package christimperley.kaskara;

import java.util.ArrayList;
import java.util.List;
import spoon.reflect.code.CtStatement;
import spoon.reflect.visitor.filter.AbstractFilter;

/**
 * Provides an interface for finding all statements within a given project.
 */
public class StatementFinder {
    private final Project project;

    public static StatementFinder forProject(Project project) {
        return new StatementFinder(project);
    }

    protected StatementFinder(Project project) {
        this.project = project;
    }

    /**
     * Finds all statements within the associated project.
     * @return  A list of all statements within the associated project.
     */
    public List<Statement> find() {
        var elements = this.project.getModel().getElements(new AbstractFilter<CtStatement>() {
            @Override
            public boolean matches(CtStatement element) {
                // must be a top-level statement within a block
                if (!(element.getParent() instanceof spoon.support.reflect.code.CtBlockImpl)) {
                    return false;
                }

                // ignore blocks
                if (element instanceof spoon.support.reflect.code.CtBlockImpl) {
                    return false;
                }

                // ignore comments
                if (element instanceof spoon.support.reflect.code.CtCommentImpl) {
                    return false;
                }

                // ignore class implementations
                if (element instanceof spoon.support.reflect.declaration.CtClassImpl) {
                    return false;
                }

                // statement must appear in file
                return element.getPosition().isValidPosition();
            }
        });

        List<Statement> statements = new ArrayList<>();
        for (var element : elements) {
            var statement = Statement.forSpoonStatement(element);
            statements.add(statement);
        }
        return statements;
    }
}
