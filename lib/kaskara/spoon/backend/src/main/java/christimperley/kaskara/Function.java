package christimperley.kaskara;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import spoon.reflect.cu.SourcePosition;
import spoon.reflect.declaration.CtMethod;

/**
 * Describes a function within a given project.
 */
public class Function {
    @JsonProperty("name")
    private final String name;
    @JsonSerialize(converter = SourcePositionSerializer.class)
    private final SourcePosition location;
    @JsonSerialize(converter = SourcePositionSerializer.class)
    private final SourcePosition bodyLocation;

    /**
     * Constructs a function description for a given Clang AST method element.
     * @param element   The AST element for the method.
     * @return  A description of the given AST element.
     */
    public static Function forSpoonMethod(CtMethod<?> element) {
        var name = element.getSimpleName();
        var location = element.getPosition();
        var body = element.getBody();
        var bodyLocation = body.getPosition();
        return new Function(name, location, bodyLocation);
    }

    /**
     * Constructs a function description.
     * @param name          The name of the function.
     * @param location      The location of the function definition.
     * @param bodyLocation  The location of the body of the function definition.
     */
    public Function(String name, SourcePosition location, SourcePosition bodyLocation) {
        this.name = name;
        this.location = location;
        this.bodyLocation = bodyLocation;
    }
}
