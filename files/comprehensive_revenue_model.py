"""
Comprehensive Music Revenue Model
Includes ALL revenue streams and transparent breakdowns of who gets what
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List
import json

@dataclass
class RevenueBreakdown:
    """Complete revenue breakdown for a song"""
    # Total revenue
    total_gross_revenue: float
    
    # Streaming revenue
    streaming_revenue: float
    streaming_platform_cut: float  # 25-30%
    streaming_to_rights_holders: float  # 70-75%
    
    # Physical sales revenue
    physical_sales_revenue: float
    physical_distribution_cut: float  # 15-25%
    physical_to_rights_holders: float
    
    # Tour revenue (driven by hit songs)
    tour_revenue: float
    tour_venue_cut: float  # 20-30%
    tour_to_artist: float
    
    # Merchandise revenue
    merchandise_revenue: float
    merchandise_costs: float  # 40-50%
    merchandise_to_artist: float
    
    # Rights holder distribution (from streaming + physical)
    total_to_rights_holders: float
    label_share: float  # 58-80% of rights holder money
    artist_share_before_deductions: float  # 16-21% of rights holder money
    songwriter_share: float  # 10.5% of rights holder money  
    publisher_share: float  # 4.5% of rights holder money
    producer_share: float  # 3-5% of rights holder money
    
    # Final artist take-home
    manager_cut: float  # 15-20% of artist earnings
    artist_final_net: float
    
    # Label & others final
    label_final_net: float
    producer_final_net: float
    songwriter_final_net: float
    publisher_final_net: float


class ComprehensiveRevenueModel:
    """
    Complete revenue model accounting for:
    1. Streaming revenue
    2. Physical sales (vinyl/CD boost for hits)
    3. Tour revenue multiplier (hits drive tour sales)
    4. Merchandise revenue (hits boost merch sales)
    5. Full breakdown of who gets what
    """
    
    def __init__(self):
        """Initialize with research-backed percentages"""
        
        # Platform cuts (DSP = Digital Service Provider)
        self.spotify_cut = 0.27  # Spotify keeps ~27%
        self.physical_distributor_cut = 0.20  # 20% for physical distribution
        
        # Rights holder split (from what DSP pays out)
        self.label_percentage = 0.64  # Label gets 64% of rights holder money
        self.artist_percentage = 0.16  # Artist gets 16% (before manager)
        self.songwriter_percentage = 0.105  # Songwriter gets 10.5%
        self.publisher_percentage = 0.045  # Publisher gets 4.5%
        self.producer_percentage = 0.04  # Producer gets 4%
        
        # Deductions from artist share
        self.manager_percentage = 0.18  # Manager takes 15-20%, use 18%
        
        # Tour economics
        self.tour_venue_cut = 0.25  # Venue/promoter takes 25%
        
        # Merchandise economics
        self.merch_cost_percentage = 0.45  # 45% goes to production/shipping
        
        # Streaming rates (per stream, total to rights holders)
        self.avg_stream_payout = 0.004  # $0.004 per stream average
        
    def estimate_streams_from_popularity(self, popularity: int) -> int:
        """
        Estimate lifetime streams based on popularity score
        
        Research shows:
        - 100 pop: 1-7+ billion streams (mega hits)
        - 90 pop: 500M-3B streams (major hits)
        - 80 pop: 100-500M streams (hits)
        - 70 pop: 50-100M streams (good)
        - 50 pop: 10-50M streams (average)
        - 30 pop: 2-10M streams (low)
        - 10 pop: 100K-2M streams (minimal)
        - 0 pop: <100K streams
        """
        
        if popularity >= 95:
            streams = 5000000000  # 5 billion
        elif popularity >= 90:
            streams = 2000000000  # 2 billion
        elif popularity >= 85:
            streams = 500000000   # 500 million
        elif popularity >= 80:
            streams = 200000000   # 200 million
        elif popularity >= 75:
            streams = 100000000   # 100 million
        elif popularity >= 70:
            streams = 60000000    # 60 million
        elif popularity >= 65:
            streams = 35000000    # 35 million
        elif popularity >= 60:
            streams = 20000000    # 20 million
        elif popularity >= 55:
            streams = 12000000    # 12 million
        elif popularity >= 50:
            streams = 7000000     # 7 million
        elif popularity >= 45:
            streams = 4000000     # 4 million
        elif popularity >= 40:
            streams = 2500000     # 2.5 million
        elif popularity >= 35:
            streams = 1500000     # 1.5 million
        elif popularity >= 30:
            streams = 800000      # 800K
        elif popularity >= 25:
            streams = 400000      # 400K
        elif popularity >= 20:
            streams = 200000      # 200K
        elif popularity >= 15:
            streams = 100000      # 100K
        elif popularity >= 10:
            streams = 50000       # 50K
        elif popularity >= 5:
            streams = 20000       # 20K
        else:
            streams = 5000        # 5K
        
        return streams
    
    def calculate_physical_sales_multiplier(self, popularity: int) -> float:
        """
        Calculate physical sales revenue as multiplier of streaming
        
        Hit songs drive vinyl/CD purchases more than mid-tier songs
        """
        if popularity >= 90:
            return 0.25  # Major hits: 25% of streaming revenue in physical
        elif popularity >= 80:
            return 0.18  # Hits: 18%
        elif popularity >= 70:
            return 0.12  # Good songs: 12%
        elif popularity >= 50:
            return 0.08  # Average: 8%
        elif popularity >= 35:
            return 0.05  # Mid: 5%
        else:
            return 0.02  # Bust: 2%
    
    def calculate_tour_revenue_multiplier(self, popularity: int) -> float:
        """
        Calculate tour revenue driven by song popularity
        
        Research shows: 90%+ of top artist income comes from tours
        Hit songs drive tour ticket sales significantly
        """
        if popularity >= 90:
            return 8.0  # Mega hits drive 8x streaming revenue in tour sales
        elif popularity >= 80:
            return 5.0  # Hits drive 5x
        elif popularity >= 70:
            return 3.0  # Good songs drive 3x
        elif popularity >= 60:
            return 1.5  # Above average: 1.5x
        elif popularity >= 50:
            return 0.8  # Average: 0.8x
        elif popularity >= 35:
            return 0.3  # Mid: 0.3x
        else:
            return 0.1  # Bust: 0.1x
    
    def calculate_merchandise_multiplier(self, popularity: int) -> float:
        """
        Calculate merchandise revenue driven by song popularity
        
        Hit songs boost merch sales at concerts and online
        """
        if popularity >= 90:
            return 2.0  # Mega hits: 2x streaming revenue in merch
        elif popularity >= 80:
            return 1.3  # Hits: 1.3x
        elif popularity >= 70:
            return 0.8  # Good: 0.8x
        elif popularity >= 60:
            return 0.5  # Above average: 0.5x
        elif popularity >= 50:
            return 0.3  # Average: 0.3x
        elif popularity >= 35:
            return 0.15  # Mid: 0.15x
        else:
            return 0.05  # Bust: 0.05x
    
    def calculate_comprehensive_revenue(self, popularity: int) -> RevenueBreakdown:
        """
        Calculate complete revenue breakdown for a song
        
        Args:
            popularity: Song popularity score (0-100)
            
        Returns:
            RevenueBreakdown with all revenue streams and splits
        """
        
        if pd.isna(popularity):
            popularity = 0
        
        # 1. STREAMING REVENUE
        streams = self.estimate_streams_from_popularity(int(popularity))
        streaming_revenue = streams * self.avg_stream_payout
        
        # Platform takes its cut
        platform_cut = streaming_revenue * self.spotify_cut
        streaming_to_rights = streaming_revenue * (1 - self.spotify_cut)
        
        # 2. PHYSICAL SALES REVENUE
        physical_multiplier = self.calculate_physical_sales_multiplier(popularity)
        physical_gross = streaming_revenue * physical_multiplier
        physical_distribution = physical_gross * self.physical_distributor_cut
        physical_to_rights = physical_gross * (1 - self.physical_distributor_cut)
        
        # 3. TOTAL TO RIGHTS HOLDERS (streaming + physical)
        total_to_rights_holders = streaming_to_rights + physical_to_rights
        
        # Split among rights holders
        label_share = total_to_rights_holders * self.label_percentage
        artist_share_gross = total_to_rights_holders * self.artist_percentage
        songwriter_share = total_to_rights_holders * self.songwriter_percentage
        publisher_share = total_to_rights_holders * self.publisher_percentage
        producer_share = total_to_rights_holders * self.producer_percentage
        
        # 4. TOUR REVENUE (artist keeps more of this)
        tour_multiplier = self.calculate_tour_revenue_multiplier(popularity)
        tour_gross = streaming_revenue * tour_multiplier
        tour_venue_cut = tour_gross * self.tour_venue_cut
        tour_to_artist = tour_gross * (1 - self.tour_venue_cut)
        
        # 5. MERCHANDISE REVENUE
        merch_multiplier = self.calculate_merchandise_multiplier(popularity)
        merch_gross = streaming_revenue * merch_multiplier
        merch_costs = merch_gross * self.merch_cost_percentage
        merch_to_artist = merch_gross * (1 - self.merch_cost_percentage)
        
        # 6. ARTIST FINAL CALCULATIONS
        # Artist gets: recorded music share + tour + merch
        artist_total_before_manager = artist_share_gross + tour_to_artist + merch_to_artist
        manager_cut = artist_total_before_manager * self.manager_percentage
        artist_final_net = artist_total_before_manager * (1 - self.manager_percentage)
        
        # 7. TOTAL GROSS REVENUE
        total_gross = (streaming_revenue + physical_gross + 
                      tour_gross + merch_gross)
        
        return RevenueBreakdown(
            total_gross_revenue=total_gross,
            
            streaming_revenue=streaming_revenue,
            streaming_platform_cut=platform_cut,
            streaming_to_rights_holders=streaming_to_rights,
            
            physical_sales_revenue=physical_gross,
            physical_distribution_cut=physical_distribution,
            physical_to_rights_holders=physical_to_rights,
            
            tour_revenue=tour_gross,
            tour_venue_cut=tour_venue_cut,
            tour_to_artist=tour_to_artist,
            
            merchandise_revenue=merch_gross,
            merchandise_costs=merch_costs,
            merchandise_to_artist=merch_to_artist,
            
            total_to_rights_holders=total_to_rights_holders,
            label_share=label_share,
            artist_share_before_deductions=artist_share_gross,
            songwriter_share=songwriter_share,
            publisher_share=publisher_share,
            producer_share=producer_share,
            
            manager_cut=manager_cut,
            artist_final_net=artist_final_net,
            
            label_final_net=label_share,
            producer_final_net=producer_share,
            songwriter_final_net=songwriter_share,
            publisher_final_net=publisher_share
        )
    
    def print_breakdown(self, popularity: int, song_title: str = "Example Song"):
        """Print detailed revenue breakdown for a song"""
        
        breakdown = self.calculate_comprehensive_revenue(popularity)
        
        print("\n" + "="*80)
        print(f"COMPREHENSIVE REVENUE BREAKDOWN: {song_title}")
        print(f"Popularity Score: {popularity}")
        print("="*80)
        
        print(f"\n💰 TOTAL GROSS REVENUE: ${breakdown.total_gross_revenue:,.2f}")
        print("-" * 80)
        
        print("\n📊 REVENUE BY SOURCE:")
        print(f"  Streaming:     ${breakdown.streaming_revenue:>15,.2f} ({breakdown.streaming_revenue/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  Physical:      ${breakdown.physical_sales_revenue:>15,.2f} ({breakdown.physical_sales_revenue/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  Tours:         ${breakdown.tour_revenue:>15,.2f} ({breakdown.tour_revenue/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  Merchandise:   ${breakdown.merchandise_revenue:>15,.2f} ({breakdown.merchandise_revenue/breakdown.total_gross_revenue*100:>5.1f}%)")
        
        print("\n💸 DEDUCTIONS:")
        print(f"  Platform Cut:  ${breakdown.streaming_platform_cut:>15,.2f} (Spotify/Apple/etc.)")
        print(f"  Distribution:  ${breakdown.physical_distribution_cut:>15,.2f} (Physical distributors)")
        print(f"  Venue/Promoter:${breakdown.tour_venue_cut:>15,.2f} (Tour venues)")
        print(f"  Merch Costs:   ${breakdown.merchandise_costs:>15,.2f} (Production/shipping)")
        
        print("\n👥 FINAL DISTRIBUTION TO PARTIES:")
        print(f"  🏢 Label:      ${breakdown.label_final_net:>15,.2f} ({breakdown.label_final_net/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  🎤 Artist:     ${breakdown.artist_final_net:>15,.2f} ({breakdown.artist_final_net/breakdown.total_gross_revenue*100:>5.1f}%) [after manager]")
        print(f"  📝 Songwriter: ${breakdown.songwriter_final_net:>15,.2f} ({breakdown.songwriter_final_net/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  📚 Publisher:  ${breakdown.publisher_final_net:>15,.2f} ({breakdown.publisher_final_net/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  🎛️  Producer:   ${breakdown.producer_final_net:>15,.2f} ({breakdown.producer_final_net/breakdown.total_gross_revenue*100:>5.1f}%)")
        print(f"  👔 Manager:    ${breakdown.manager_cut:>15,.2f} ({breakdown.manager_cut/breakdown.total_gross_revenue*100:>5.1f}%)")
        
        print("\n📈 BREAKDOWN NOTES:")
        print(f"  • Streaming: {self.estimate_streams_from_popularity(popularity):,} estimated streams")
        print(f"  • Platform keeps ~27% of streaming revenue")
        print(f"  • Label gets largest share of recording rights (~64%)")
        print(f"  • Artist keeps more from tours/merch than streaming")
        print(f"  • Hit songs (80+) drive significant tour & merch revenue")
        
        print("="*80 + "\n")


def test_revenue_model():
    """Test the comprehensive revenue model with reference songs"""
    
    model = ComprehensiveRevenueModel()
    
    test_songs = [
        (100, "HIT ME HARD AND SOFT - Billie Eilish"),
        (90, "One Dance - Drake"),
        (80, "Cash n Gas - Kaash Paige"),
        (70, "That Just Isn't Empirically Possible - $uicideboy$"),
        (50, "Whoa in Woeful - $uicideboy$"),
        (30, "Skipper Dan - Weird Al"),
        (10, "Confidence - Mayday"),
        (0, "A Very Bieber Christmas - #1 Holiday Carolers")
    ]
    
    for pop, title in test_songs:
        model.print_breakdown(pop, title)


if __name__ == "__main__":
    test_revenue_model()
