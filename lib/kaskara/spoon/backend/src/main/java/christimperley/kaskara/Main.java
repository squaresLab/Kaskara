package christimperley.kaskara;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import picocli.CommandLine;
import spoon.reflect.code.CtStatement;
import spoon.reflect.visitor.filter.AbstractFilter;


@CommandLine.Command(name = "kaskara", mixinStandardHelpOptions = true)
public class Main implements Callable<Integer> {
    @CommandLine.Parameters(index = "0",
            description = "The root source code directory for the project.")
    private String directory;

    @CommandLine.Option(names = "-o",
        defaultValue = ".",
        description = "The directory to which results should be written.")
    private String outputDirectory;

    /**
     * Provides an entrypoint to the Kaskara Java analysis tool.
     *
     * @param args  A list of command-line arguments.
     */
    public static void main(String[] args) throws IOException {
        System.exit(new CommandLine(new Main()).execute(args));
    }

    /**
     * Prepares the output directory by ensuring that it exists.
     */
    private void prepareOutputDirectory() throws IOException {
        this.outputDirectory = FileSystems.getDefault()
                .getPath(this.outputDirectory)
                .normalize()
                .toAbsolutePath()
                .toString();

        Files.createDirectories(Paths.get(this.outputDirectory));
        System.out.printf("Output will be written to: %s%n", this.outputDirectory);
    }

    @Override
    public Integer call() throws IOException {
        try {
            this.prepareOutputDirectory();
        } catch (java.nio.file.AccessDeniedException exc) {
            System.err.printf("ERROR: insufficient permissions to write to output directory [%s]%n",
                    this.outputDirectory);
            return 1;
        }

        // construct a description of the project
        var project = Project.build(this.directory);

        // find all statements in the program
        var elements = project.getModel().getElements(new AbstractFilter<CtStatement>() {
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

        var statementsFileName = Path.of(this.outputDirectory, "statements.json").toString();
        var mapper = new ObjectMapper();
        mapper.enable(SerializationFeature.INDENT_OUTPUT);
        try (var fileOutputStream = new FileOutputStream(statementsFileName)) {
            mapper.writeValue(fileOutputStream, statements);
        }

        return 0;
    }
}
