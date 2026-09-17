"""
Tests for Profiled Workload Fingerprint Analysis
-------------------------------------------------
Tests the database-backed workload analysis introduced
in M12.3.

These tests verify:

- Query profiles can be loaded.
- Profiles are grouped using query fingerprints.
- Structurally equivalent profiles are grouped together.
- Q009 profiles 10 and 17 are consolidated.
- Execution counts and rows are aggregated correctly.
- Weighted average execution time is calculated correctly.
- Groups are ordered by total execution time.
"""

import unittest

from collector.workload_analyzer import (
    analyze_profiled_workload,
)


class TestProfiledWorkloadAnalyzer(
    unittest.TestCase
):

    @classmethod
    def setUpClass(cls):
        """
        Run the database-backed analysis once for
        the entire test class.
        """

        cls.analysis = (
            analyze_profiled_workload()
        )

    # =====================================================
    # BASIC PROFILE COUNTS
    # =====================================================

    def test_total_profiles(self):
        """
        The current database contains 16 query profiles.
        """

        self.assertEqual(
            self.analysis["total_profiles"],
            16,
        )

    def test_unique_fingerprints(self):
        """
        The 16 profiles currently represent 15
        structural query fingerprints.
        """

        self.assertEqual(
            self.analysis[
                "unique_fingerprints"
            ],
            15,
        )

    # =====================================================
    # EXECUTION AGGREGATION
    # =====================================================

    def test_total_executions(self):
        """
        Execution counts from all profiles should
        aggregate correctly.
        """

        self.assertEqual(
            self.analysis[
                "total_executions"
            ],
            18,
        )

    def test_total_rows_processed(self):
        """
        Rows processed should be aggregated across
        all profile records.
        """

        self.assertEqual(
            self.analysis[
                "total_rows_processed"
            ],
            85343,
        )

    # =====================================================
    # Q009 FINGERPRINT GROUPING
    # =====================================================

    def test_q009_profiles_are_grouped(self):
        """
        Profiles 10 and 17 represent the same Q009
        query structure despite formatting differences.

        They must therefore belong to one fingerprint
        group.
        """

        q009_group = None

        for group in self.analysis[
            "groups"
        ]:

            profile_ids = set(
                group["profile_ids"]
            )

            if {
                10,
                17,
            }.issubset(profile_ids):

                q009_group = group
                break

        self.assertIsNotNone(
            q009_group
        )

        self.assertEqual(
            set(q009_group["profile_ids"]),
            {10, 17},
        )

    def test_q009_execution_aggregation(self):
        """
        Profiles 10 and 17 together represent
        three executions.
        """

        q009_group = self._get_q009_group()

        self.assertEqual(
            q009_group[
                "total_executions"
            ],
            3,
        )

    def test_q009_rows_aggregation(self):
        """
        Profile 10 processed 7957 rows and profile 17
        processed 7957 rows.

        The grouped total should therefore be 15914.
        """

        q009_group = self._get_q009_group()

        self.assertEqual(
            q009_group[
                "total_rows_processed"
            ],
            15914,
        )

    def test_q009_execution_time_aggregation(self):
        """
        The grouped Q009 execution time should equal
        the sum of profiles 10 and 17.
        """

        q009_group = self._get_q009_group()

        self.assertAlmostEqual(
            q009_group[
                "total_execution_time_ms"
            ],
            1492.131,
            places=3,
        )

    def test_q009_weighted_average(self):
        """
        Weighted average execution time should be:

            total execution time
            ---------------------
             total executions
        """

        q009_group = self._get_q009_group()

        expected_average = (
            q009_group[
                "total_execution_time_ms"
            ]
            / q009_group[
                "total_executions"
            ]
        )

        self.assertAlmostEqual(
            q009_group[
                "weighted_average_execution_time_ms"
            ],
            expected_average,
            places=6,
        )

    # =====================================================
    # GROUP SORTING
    # =====================================================

    def test_groups_sorted_by_total_execution_time(
        self
    ):
        """
        Fingerprint groups should be ordered from
        highest to lowest total execution time.
        """

        groups = self.analysis[
            "groups"
        ]

        execution_times = [
            group[
                "total_execution_time_ms"
            ]
            for group in groups
        ]

        self.assertEqual(
            execution_times,
            sorted(
                execution_times,
                reverse=True,
            ),
        )

    # =====================================================
    # HELPER
    # =====================================================

    def _get_q009_group(self):
        """
        Return the fingerprint group containing
        profiles 10 and 17.
        """

        for group in self.analysis[
            "groups"
        ]:

            profile_ids = set(
                group["profile_ids"]
            )

            if {
                10,
                17,
            }.issubset(profile_ids):

                return group

        self.fail(
            "Q009 fingerprint group "
            "containing profiles 10 and 17 "
            "was not found."
        )


# =========================================================
# SCRIPT ENTRY POINT
# =========================================================

if __name__ == "__main__":
    unittest.main()
