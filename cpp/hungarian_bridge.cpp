#include <vector>
#include <limits>
#include <algorithm>
#include <cmath>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

static std::vector<int> hungarian_square(const std::vector<double>& a, int n) {
    const double INF = 1e18;

    std::vector<double> u(n + 1, 0.0), v(n + 1, 0.0);
    std::vector<int> p(n + 1, 0), way(n + 1, 0);

    for (int i = 1; i <= n; ++i) {
        p[0] = i;
        int j0 = 0;
        std::vector<double> minv(n + 1, INF);
        std::vector<bool> used(n + 1, false);

        do {
            used[j0] = true;
            int i0 = p[j0];
            double delta = INF;
            int j1 = 0;

            for (int j = 1; j <= n; ++j) {
                if (!used[j]) {
                    double cur = a[(i0 - 1) * n + (j - 1)] - u[i0] - v[j];
                    if (cur < minv[j]) {
                        minv[j] = cur;
                        way[j] = j0;
                    }
                    if (minv[j] < delta) {
                        delta = minv[j];
                        j1 = j;
                    }
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
            int j1 = way[j0];
            p[j0] = p[j1];
            j0 = j1;
        } while (j0);
    }

    std::vector<int> assignment(n, -1);
    for (int j = 1; j <= n; ++j) {
        if (p[j] != 0) {
            assignment[p[j] - 1] = j - 1;
        }
    }

    return assignment;
}

extern "C" EXPORT int solve_assignment(
    const double* cost_matrix,
    int rows,
    int cols,
    double max_cost,
    int* assignment_out
) {
    if (!cost_matrix || !assignment_out || rows < 0 || cols < 0) {
        return -1;
    }

    if (rows == 0) {
        return 0;
    }

    int n = std::max(rows, cols);
    double pad_cost = max_cost + 1e6;

    std::vector<double> square_cost(n * n, pad_cost);

    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            square_cost[r * n + c] = cost_matrix[r * cols + c];
        }
    }

    std::vector<int> square_assignment = hungarian_square(square_cost, n);

    for (int r = 0; r < rows; ++r) {
        int c = square_assignment[r];
        if (c >= cols) {
            assignment_out[r] = -1;
        } else {
            double assigned_cost = cost_matrix[r * cols + c];
            if (assigned_cost <= max_cost) {
                assignment_out[r] = c;
            } else {
                assignment_out[r] = -1;
            }
        }
    }

    return 0;
}