package christimperley.kaskara;

import com.fasterxml.jackson.databind.util.StdConverter;
import spoon.reflect.cu.SourcePosition;

public class SourcePositionSerializer extends StdConverter<SourcePosition, String> {
    @Override
    public String convert(SourcePosition value) {
        return String.format("%s@%d:%d::%d:%d",
                value.getFile().getAbsolutePath(),
                value.getLine(),
                value.getColumn(),
                value.getEndLine(),
                value.getEndColumn());
    }
}
