package christimperley.kaskara;

import spoon.reflect.code.CtStatement;
import spoon.reflect.cu.SourcePosition;

/**
 * Provides a summary of a single program statement.
 */
public final class Statement {
    private final String source;
    private final SourcePosition position;

    /**
     * Produces a description of a statement given its corresponding Spoon AST element.
     * @param element The AST element for the statement.
     * @return A description of the statement associated with that element.
     */
    public static Statement forSpoonStatement(CtStatement element) {
        var source = element.toString();
        var position = element.getPosition();
        return new Statement(source, position);
    }

    public Statement(String source, SourcePosition position) {
        this.source = source;
        this.position = position;
    }

    @Override
    public boolean equals(Object other) {
        if (!(other instanceof Statement)) {
            return false;
        }
        Statement statement = (Statement) other;
        return this.source.equals(statement.source) && this.position.equals(statement.position);
    }

    @Override
    public String toString() {
        return String.format("Statement[Position: %s; Content: \"%s\"]",
                             this.position, this.source);
    }
}
