package christimperley.kaskara;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import spoon.reflect.code.CtLoop;
import spoon.reflect.cu.SourcePosition;

/**
 * Describes a control-flow loop within a given project.
 */
public class Loop {
    @JsonSerialize(converter = SourcePositionSerializer.class)
    @JsonProperty("body")
    private final SourcePosition bodyLocation;

    /**
     * Constructs a description for a given Clang AST loop element.
     * @param element   The AST element for the loop.
     * @return  A description of the given AST element.
     */
    public static Loop forSpoonLoop(CtLoop element) {
        var bodyLocation = element.getBody().getPosition();
        return new Loop(bodyLocation);
    }

    protected Loop(SourcePosition bodyLocation) {
        this.bodyLocation = bodyLocation;
    }
}
