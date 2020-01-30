package christimperley.kaskara;

import java.util.ArrayList;
import java.util.List;
import spoon.Launcher;
import spoon.reflect.code.CtStatement;
import spoon.reflect.visitor.filter.AbstractFilter;


public class Main {
    /**
     * Provides an entrypoint to the Kaskara Java analysis tool.
     *
     * @param args  A list of command-line arguments.
     */
    public static void main(String[] args) {
        var launcher = new Launcher();
        launcher.getEnvironment().setAutoImports(true);
        // add source code directories [specify as command line argument]
        launcher.addInputResource("src/main/java/");
        var model = launcher.buildModel();

        // find all statements in the program
        var elements = model.getElements(new AbstractFilter<CtStatement>() {
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
            System.out.printf("%s%n%n", statement);
        }
    }
}
