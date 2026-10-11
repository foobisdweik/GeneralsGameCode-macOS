import Foundation

/// Wraps the installed engine in a minimal `.app` bundle so macOS treats it as
/// a game.
///
/// Game Mode needs three things: the process is an app that LaunchServices
/// launched, the app's Info.plist declares a game category, and the game binary
/// is the bundle's own executable. A bare `runtime/generalszh` started with
/// `Process()` is an anonymous process to the system (`anon<generalszh>`), so
/// `gamepolicyd` never considers it a game.
///
/// The release payload stays a flat directory. The bundle is assembled from it
/// on demand, and rebuilt whenever the installed binary changes.
enum GameBundle {
    static let bundleIdentifier = "com.dvcdsys.GeneralsZH.game"

    static var url: URL {
        Config.runtimeDir.appendingPathComponent("GeneralsZH.app", isDirectory: true)
    }

    private static var macOSDir: URL {
        url.appendingPathComponent("Contents/MacOS", isDirectory: true)
    }

    static var executable: URL {
        macOSDir.appendingPathComponent(Config.binaryName)
    }

    /// Builds the bundle if it is missing or older than the installed binary.
    /// Returns the bundle URL.
    @discardableResult
    static func ensure() throws -> URL {
        let fm = FileManager.default
        let source = Config.runtimeBinary
        guard fm.fileExists(atPath: source.path) else {
            throw LauncherError.binaryMissingAfterInstall
        }
        if isCurrent(source: source) { return url }

        if fm.fileExists(atPath: url.path) {
            try fm.removeItem(at: url)
        }
        try fm.createDirectory(at: macOSDir, withIntermediateDirectories: true)

        // The binary finds its dylibs through @loader_path, so they go next to it.
        // copyItem keeps the dylib version symlinks as symlinks.
        try fm.copyItem(at: source, to: executable)
        let entries = try fm.contentsOfDirectory(atPath: Config.runtimeDir.path)
        for name in entries where name.hasSuffix(".dylib") {
            try fm.copyItem(at: Config.runtimeDir.appendingPathComponent(name),
                            to: macOSDir.appendingPathComponent(name))
        }

        // Stamp the copy with the source's date, so isCurrent can detect an update.
        if let date = try fm.attributesOfItem(atPath: source.path)[.modificationDate] as? Date {
            try fm.setAttributes([.modificationDate: date], ofItemAtPath: executable.path)
        }

        try writeInfoPlist()
        return url
    }

    private static func isCurrent(source: URL) -> Bool {
        let fm = FileManager.default
        guard let src = try? fm.attributesOfItem(atPath: source.path),
              let dst = try? fm.attributesOfItem(atPath: executable.path),
              fm.fileExists(atPath: url.appendingPathComponent("Contents/Info.plist").path)
        else { return false }
        return (src[.size] as? NSNumber) == (dst[.size] as? NSNumber)
            && (src[.modificationDate] as? Date) == (dst[.modificationDate] as? Date)
    }

    private static func writeInfoPlist() throws {
        let version = (try? String(contentsOf: Config.versionFile, encoding: .utf8))?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? "0"
        let plist: [String: Any] = [
            "CFBundleIdentifier": bundleIdentifier,
            "CFBundleName": "Generals Zero Hour",
            "CFBundleDisplayName": "Generals Zero Hour",
            "CFBundleExecutable": Config.binaryName,
            "CFBundlePackageType": "APPL",
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundleShortVersionString": version,
            "CFBundleVersion": version,
            "LSMinimumSystemVersion": "12.0",
            // Game Mode: the category marks the app as a game. GCSupportsGameMode
            // opts in explicitly.
            "LSApplicationCategoryType": "public.app-category.strategy-games",
            "GCSupportsGameMode": true,
            "NSHighResolutionCapable": true,
        ]
        let data = try PropertyListSerialization.data(fromPropertyList: plist,
                                                      format: .xml, options: 0)
        try data.write(to: url.appendingPathComponent("Contents/Info.plist"))
    }
}
