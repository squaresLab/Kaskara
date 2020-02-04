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

    private ObjectMapper mapper;

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

    /**
     * Finds all statements within the project and writes a summary of those statements
     * to disk.
     * @throws IOException  If an error occurs during the write to disk.
     */
    private void findStatements(Project project) throws IOException {
        System.out.println("Finding all statements in project");
        var statementsFileName = Path.of(this.outputDirectory, "statements.json").toString();
        var statements = StatementFinder.forProject(project).find();
        try (var fileOutputStream = new FileOutputStream(statementsFileName)) {
            this.mapper.writeValue(fileOutputStream, statements);
        }
        System.out.printf("Wrote summary of statements to disk [%s]%n",  statementsFileName);
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

        // prepare the JSON output formatter
        this.mapper = new ObjectMapper();
        this.mapper.enable(SerializationFeature.INDENT_OUTPUT);

        var project = Project.build(this.directory);
        this.findStatements(project);
        return 0;
    }
}
