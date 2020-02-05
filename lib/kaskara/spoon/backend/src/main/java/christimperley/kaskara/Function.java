package christimperley.kaskara;

import com.fasterxml.jackson.annotation.JsonGetter;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import spoon.reflect.cu.SourcePosition;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.reference.CtTypeReference;

/**
 * Describes a function within a given project.
 */
public class Function {
    @JsonProperty("name")
    private final String name;
    @JsonSerialize(converter = SourcePositionSerializer.class)
    @JsonProperty("location")
    private final SourcePosition location;
    @JsonSerialize(converter = SourcePositionSerializer.class)
    @JsonProperty("body")
    private final SourcePosition bodyLocation;
    private final CtTypeReference<?> returnType;

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
        var returnType = element.getType();
        return new Function(name, location, bodyLocation, returnType);
    }

    /**
     * Constructs a function description.
     * @param name          The name of the function.
     * @param location      The location of the function definition.
     * @param bodyLocation  The location of the body of the function definition.
     * @param returnType    The return type of the function.
     */
    public Function(String name,
                    SourcePosition location,
                    SourcePosition bodyLocation,
                    CtTypeReference<?> returnType) {
        this.name = name;
        this.location = location;
        this.bodyLocation = bodyLocation;
        this.returnType = returnType;
    }

    @JsonGetter("return-type")
    public String getReturnType() {
        return this.returnType.getQualifiedName();
    }
}
