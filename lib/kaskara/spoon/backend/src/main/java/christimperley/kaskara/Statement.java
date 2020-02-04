package christimperley.kaskara;

import com.fasterxml.jackson.annotation.JsonGetter;
import spoon.reflect.code.CtStatement;
import spoon.reflect.cu.SourcePosition;


/**
 * Provides a summary of a single program statement.
 */
public final class Statement {
    private final Class kind;
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
        var kind = element.getClass();
        return new Statement(kind, source, position);
    }

    /**
     * Constructs a Statement description.
     * @param kind      The class that represents the corresponding AST element for this statement.
     * @param source    The original source code for the statement.
     * @param position  The position of this statement.
     */
    public Statement(Class kind, String source, SourcePosition position) {
        this.kind = kind;
        this.source = source;
        this.position = position;
    }

    @JsonGetter("kind")
    public String getKind() {
        return this.kind.getName();
    }

    @JsonGetter("source")
    public String getSource() {
        return this.source;
    }

    /**
     * Returns the position of statement as a string.
     * @return A string encoding of the position of the statement.
     */
    @JsonGetter("position")
    public String getPositionAsString() {
        var filename = this.position.getFile();
        var startLine = this.position.getLine();
        var startCol = this.position.getColumn();
        var endLine = this.position.getEndLine();
        var endCol = this.position.getEndColumn();
        return String.format("%s@%d:%d::%d:%d",
                this.position.getFile().getAbsolutePath(),
                this.position.getLine(),
                this.position.getColumn(),
                this.position.getEndLine(),
                this.position.getEndColumn());
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
