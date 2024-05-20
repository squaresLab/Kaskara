package christimperley.kaskara;

import com.fasterxml.jackson.annotation.JsonGetter;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import spoon.reflect.code.CtStatement;
import spoon.reflect.cu.SourcePosition;


/**
 * Provides a summary of a single program statement.
 */
public final class Statement {
    private final Class kind;
    @JsonProperty("source")
    private final String source;

    @JsonSerialize(converter = SourcePositionSerializer.class)
    @JsonProperty("location")
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

    /**
     * Returns the canonical form of the source for the statement.
     * @return  canonicalised source code
     */
    @JsonGetter("canonical")
    public String getCanonicalSource() {
        return this.source;
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
