#!/usr/bin/env python3
"""
Test advanced shard statistics features in Pyfinity
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pyfinity import InfinityClient, SyncInfinityClient, InfinityAPIError


class TestAdvancedShardFeatures:
    """Test cases for advanced shard statistics features."""
    
    def test_calculate_shard_stats(self):
        """Test shard statistics calculation utility."""
        client = InfinityClient("test_token", "123456789")
        
        # Test even distribution
        stats = client.calculate_shard_stats(1000, 50000, [0, 1, 2, 3])
        
        expected = {
            0: {"servers": 250, "users": 12500},
            1: {"servers": 250, "users": 12500},
            2: {"servers": 250, "users": 12500},
            3: {"servers": 250, "users": 12500}
        }
        
        assert stats == expected
    
    def test_calculate_shard_stats_with_remainder(self):
        """Test shard calculation with remainder distribution."""
        client = InfinityClient("test_token", "123456789")
        
        # Test uneven distribution
        stats = client.calculate_shard_stats(100, 2500, [0, 1, 2])
        
        # First shard should get the remainder
        assert stats[0]["servers"] == 34  # 100 // 3 + 1
        assert stats[1]["servers"] == 33  # 100 // 3
        assert stats[2]["servers"] == 33  # 100 // 3
        
        assert stats[0]["users"] == 834   # 2500 // 3 + 1
        assert stats[1]["users"] == 833   # 2500 // 3
        assert stats[2]["users"] == 833   # 2500 // 3
    
    def test_calculate_shard_stats_empty_list(self):
        """Test shard calculation with empty shard list."""
        client = InfinityClient("test_token", "123456789")
        
        stats = client.calculate_shard_stats(1000, 50000, [])
        assert stats == {}
    
    def test_analyze_shard_distribution(self):
        """Test shard distribution analysis."""
        client = InfinityClient("test_token", "123456789")
        
        shard_stats = {
            0: {"servers": 100, "users": 2000},
            1: {"servers": 120, "users": 2400},
            2: {"servers": 80, "users": 1600}
        }
        
        analysis = client.analyze_shard_distribution(shard_stats)
        
        # Check summary
        assert analysis["summary"]["total_shards"] == 3
        assert analysis["summary"]["total_servers"] == 300
        assert analysis["summary"]["total_users"] == 6000
        assert analysis["summary"]["avg_servers_per_shard"] == 100.0
        assert analysis["summary"]["avg_users_per_shard"] == 2000.0
        
        # Check distribution
        assert analysis["distribution"]["min_servers"] == 80
        assert analysis["distribution"]["max_servers"] == 120
        assert analysis["distribution"]["min_users"] == 1600
        assert analysis["distribution"]["max_users"] == 2400
        
        # Check insights
        assert analysis["insights"]["most_loaded_shard"] == 1
        assert analysis["insights"]["least_loaded_shard"] == 2
    
    def test_analyze_shard_distribution_empty(self):
        """Test shard analysis with empty data."""
        client = InfinityClient("test_token", "123456789")
        
        analysis = client.analyze_shard_distribution({})
        assert "error" in analysis
    
    def test_generate_shard_report(self):
        """Test shard report generation."""
        client = InfinityClient("test_token", "123456789")
        
        shard_stats = {
            0: {"servers": 100, "users": 2000},
            1: {"servers": 120, "users": 2400}
        }
        
        report = client.generate_shard_report(shard_stats)
        
        # Check that report contains expected sections
        assert "SHARD STATISTICS REPORT" in report
        assert "Total Shards: 2" in report
        assert "Total Servers: 220" in report
        assert "Total Users: 4,400" in report
        assert "PER-SHARD BREAKDOWN" in report
        assert "Shard 0: 100 servers, 2,000 users" in report
        assert "Shard 1: 120 servers, 2,400 users" in report
    
    def test_generate_shard_report_empty(self):
        """Test shard report with empty data."""
        client = InfinityClient("test_token", "123456789")
        
        report = client.generate_shard_report({})
        assert report == "No shard statistics available"
    
    @pytest.mark.asyncio
    async def test_post_batch_shard_stats(self):
        """Test batch shard statistics posting."""
        client = InfinityClient("test_token", "123456789")
        
        shard_stats = {
            0: {"servers": 100, "users": 2000},
            1: {"servers": 120, "users": 2400}
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            response = await client.post_batch_shard_stats(shard_stats)
            
            mock_request.assert_called_once_with(
                "POST",
                "/bots/123456789/stats/batch",
                data={"shard_stats": shard_stats}
            )
            assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_all_shard_info(self):
        """Test getting all shard information."""
        client = InfinityClient("test_token", "123456789")
        
        expected_info = {
            "shards": [
                {"id": 0, "servers": 100, "users": 2000},
                {"id": 1, "servers": 120, "users": 2400}
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = expected_info
            
            shard_info = await client.get_all_shard_info()
            
            mock_request.assert_called_once_with("GET", "/bots/123456789/shards")
            assert shard_info == expected_info
    
    @pytest.mark.asyncio
    async def test_get_shard_info(self):
        """Test getting specific shard information."""
        client = InfinityClient("test_token", "123456789")
        
        expected_info = {"id": 0, "servers": 100, "users": 2000}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = expected_info
            
            shard_info = await client.get_shard_info(0)
            
            mock_request.assert_called_once_with("GET", "/bots/123456789/shard/0")
            assert shard_info == expected_info


class TestSyncShardFeatures:
    """Test synchronous shard features."""
    
    def test_sync_post_batch_shard_stats(self):
        """Test synchronous batch shard statistics posting."""
        client = SyncInfinityClient("test_token", "123456789")
        
        shard_stats = {
            0: {"servers": 100, "users": 2000},
            1: {"servers": 120, "users": 2400}
        }
        
        with patch.object(client, '_run_async') as mock_run:
            mock_run.return_value = {"success": True}
            
            response = client.post_batch_shard_stats(shard_stats)
            
            assert response["success"] is True
            mock_run.assert_called_once()
    
    def test_sync_get_all_shard_info(self):
        """Test synchronous get all shard information."""
        client = SyncInfinityClient("test_token", "123456789")
        
        expected_info = {"shards": []}
        
        with patch.object(client, '_run_async') as mock_run:
            mock_run.return_value = expected_info
            
            shard_info = client.get_all_shard_info()
            
            assert shard_info == expected_info
            mock_run.assert_called_once()
    
    def test_sync_analyze_shard_distribution(self):
        """Test synchronous shard distribution analysis."""
        client = SyncInfinityClient("test_token", "123456789")
        
        shard_stats = {
            0: {"servers": 100, "users": 2000},
            1: {"servers": 120, "users": 2400}
        }
        
        analysis = client.analyze_shard_distribution(shard_stats)
        
        assert analysis["summary"]["total_shards"] == 2
        assert analysis["summary"]["total_servers"] == 220
        assert analysis["summary"]["total_users"] == 4400
    
    def test_sync_generate_shard_report(self):
        """Test synchronous shard report generation."""
        client = SyncInfinityClient("test_token", "123456789")
        
        shard_stats = {
            0: {"servers": 100, "users": 2000}
        }
        
        report = client.generate_shard_report(shard_stats)
        
        assert "SHARD STATISTICS REPORT" in report
        assert "Total Shards: 1" in report
    
    def test_sync_calculate_shard_stats(self):
        """Test synchronous shard calculation."""
        client = SyncInfinityClient("test_token", "123456789")
        
        stats = client.calculate_shard_stats(1000, 50000, [0, 1, 2, 3])
        
        expected = {
            0: {"servers": 250, "users": 12500},
            1: {"servers": 250, "users": 12500},
            2: {"servers": 250, "users": 12500},
            3: {"servers": 250, "users": 12500}
        }
        
        assert stats == expected


# Integration test for shard workflow
class TestShardWorkflow:
    """Test complete shard workflow scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_shard_workflow(self):
        """Test a complete shard management workflow."""
        client = InfinityClient("test_token", "123456789")
        
        # Mock a complete workflow
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {"success": True}
            
            # 1. Calculate shard distribution
            shard_stats = client.calculate_shard_stats(1000, 50000, [0, 1, 2, 3])
            
            # 2. Post batch stats
            await client.post_batch_shard_stats(shard_stats)
            
            # 3. Post individual shard stats
            await client.post_shard_stats(0, 250, 12500)
            
            # 4. Get shard info
            await client.get_shard_info(0)
            
            # 5. Analyze distribution
            analysis = client.analyze_shard_distribution(shard_stats)
            
            # 6. Generate report
            report = client.generate_shard_report(shard_stats)
            
            # Verify all operations completed
            assert len(shard_stats) == 4
            assert analysis["summary"]["total_shards"] == 4
            assert "SHARD STATISTICS REPORT" in report
            assert mock_request.call_count == 3  # batch, individual, get info


# Run tests
if __name__ == "__main__":
    print("🧪 Running Advanced Shard Statistics Tests...")
    print("=" * 50)
    
    # Run with pytest
    pytest.main([__file__, "-v"])
