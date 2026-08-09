import Foundation

/// SSE client for `GET api/v1/group/moments/{id}/stream` with Bearer auth.
/// Reconnects with exponential backoff; stops permanently on 401/403/404.
final class TripMomentStreamClient {
    private var task: Task<Void, Never>?
    private var momentId: String?

    func start(
        momentId: String,
        onInvalidate: @escaping @MainActor () -> Void,
        onTerminalFailure: (@MainActor (String, Int) -> Void)? = nil
    ) {
        if self.momentId == momentId, task != nil { return }
        stop()
        self.momentId = momentId
        task = Task { [weak self] in
            var backoffNs: UInt64 = 1_000_000_000 // 1s
            let maxBackoffNs: UInt64 = 30_000_000_000
            while !Task.isCancelled {
                guard let self, let mid = self.momentId else { break }
                do {
                    try await self.runOnce(momentId: mid, onInvalidate: onInvalidate)
                    backoffNs = 1_000_000_000
                } catch is CancellationError {
                    break
                } catch let StreamTerminalError.httpStatus(code) {
                    await MainActor.run {
                        onTerminalFailure?(mid, code)
                    }
                    break
                } catch {
                    try? await Task.sleep(nanoseconds: backoffNs)
                    backoffNs = min(backoffNs * 2, maxBackoffNs)
                }
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
        momentId = nil
    }

    private enum StreamTerminalError: Error {
        case httpStatus(Int)
    }

    private func runOnce(momentId: String, onInvalidate: @escaping @MainActor () -> Void) async throws {
        var request = try APIClient.shared.buildRequest(
            path: "api/v1/group/moments/\(momentId)/stream",
            method: "GET",
            authenticated: true
        )
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 0 // long-lived SSE

        let (bytes, response) = try await URLSession.shared.bytes(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        if isGroupMomentAccessDeniedStatus(http.statusCode) {
            throw StreamTerminalError.httpStatus(http.statusCode)
        }
        guard (200 ... 299).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }

        var eventName = "message"
        var dataLines: [String] = []

        for try await line in bytes.lines {
            try Task.checkCancellation()
            if line.hasPrefix(":") {
                continue
            }
            if line.hasPrefix("event:") {
                eventName = String(line.dropFirst(6)).trimmingCharacters(in: .whitespaces)
                continue
            }
            if line.hasPrefix("data:") {
                var value = String(line.dropFirst(5))
                if value.hasPrefix(" ") { value = String(value.dropFirst()) }
                dataLines.append(value)
                continue
            }
            if line.isEmpty {
                if eventName == "invalidate", !dataLines.isEmpty {
                    await MainActor.run {
                        onInvalidate()
                    }
                }
                eventName = "message"
                dataLines.removeAll(keepingCapacity: true)
            }
        }
    }
}
