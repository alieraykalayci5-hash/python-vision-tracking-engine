// Optional native implementation for distance-gated rectangular assignment.
// Matches SciPy's augmented-cost formulation; compiles on Windows and Linux.
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

#if defined(_WIN32)
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

static std::vector<int> hungarian_square(const std::vector<double>& a, int n) {
    constexpr double INF = std::numeric_limits<double>::max() / 4.0;
    std::vector<double> u(n + 1), v(n + 1);
    std::vector<int> p(n + 1), way(n + 1);
    for (int i = 1; i <= n; ++i) {
        p[0] = i;
        int j0 = 0;
        std::vector<double> minv(n + 1, INF);
        std::vector<bool> used(n + 1, false);
        do {
            used[j0] = true;
            const int i0 = p[j0];
            double delta = INF;
            int j1 = 0;
            for (int j = 1; j <= n; ++j) {
                if (!used[j]) {
                    const double cur = a[(i0 - 1) * n + (j - 1)] - u[i0] - v[j];
                    if (cur < minv[j]) {
                        minv[j] = cur;
                        way[j] = j0;
                    }
                    if (minv[j] < delta) { delta = minv[j]; j1 = j; }
                }
            }
            for (int j = 0; j <= n; ++j) {
                if (used[j]) {
                    u[p[j]] += delta;
                    v[j] -= delta;
                } else {
                    minv[j] -= delta;
                }
            }
            j0 = j1;
        } while (p[j0] != 0);
        do {
            const int j1 = way[j0];
            p[j0] = p[j1];
            j0 = j1;
        } while (j0 != 0);
    }
    std::vector<int> result(n, -1);
    for (int j = 1; j <= n; ++j) {
        if (p[j] != 0) { result[p[j] - 1] = j - 1; }
    }
    return result;
}

extern "C" EXPORT int solve_assignment(
    const double* cost_matrix, int rows, int cols,
    double max_cost, int* assignment_out
) {
    if (!cost_matrix || !assignment_out || rows < 0 || cols < 0 ||
        !std::isfinite(max_cost) || max_cost <= 0) { return -1; }
    if (rows == 0) return 0;
    if (cols == 0) {
        for (int r = 0; r < rows; ++r) assignment_out[r] = -1;
        return 0;
    }
    const int n = rows + cols;
    if (n <= 0 || n > 20000) return -2;
    const double unmatch = (std::min(rows, cols) + 1.0) * (max_cost + 1.0);
    const double forbidden = (2.0 * n + 1.0) * unmatch;
    if (!std::isfinite(forbidden) || forbidden > 1e100) return -3;
    std::vector<double> square(static_cast<size_t>(n) * n, 0.0);
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            const double d = cost_matrix[r * cols + c];
            if (!std::isfinite(d) || d < 0.0) return -4;
            square[static_cast<size_t>(r) * n + c] =
                d <= max_cost ? d : forbidden;
        }
        for (int c = cols; c < n; ++c)
            square[static_cast<size_t>(r) * n + c] = unmatch;
    }
    for (int r = rows; r < n; ++r) {
        for (int c = 0; c < cols; ++c)
            square[static_cast<size_t>(r) * n + c] = unmatch;
    }
    const auto result = hungarian_square(square, n);
    for (int r = 0; r < rows; ++r) {
        const int c = result[r];
        assignment_out[r] =
            c >= 0 && c < cols && cost_matrix[r * cols + c] <= max_cost ? c : -1;
    }
    return 0;
}
