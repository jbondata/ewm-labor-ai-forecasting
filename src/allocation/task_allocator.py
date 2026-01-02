"""Task allocation logic for worker assignment."""

import logging
from typing import Dict, List
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class TaskAllocator:
    """Allocate workers across warehouse functions."""
    
    # Default allocation ratios
    DEFAULT_RATIOS = {
        'picking': 0.50,
        'packing': 0.30,
        'receiving': 0.20
    }
    
    def __init__(self, allocation_ratios: Optional[Dict[str, float]] = None):
        """
        Initialize task allocator.
        
        Args:
            allocation_ratios: Custom allocation ratios (must sum to 1.0)
        """
        self.ratios = allocation_ratios or self.DEFAULT_RATIOS
        
        if abs(sum(self.ratios.values()) - 1.0) > 0.01:
            raise ValueError("Allocation ratios must sum to 1.0")
    
    def allocate_workers(
        self,
        forecast_df: pd.DataFrame,
        workers_available: int
    ) -> pd.DataFrame:
        """
        Allocate workers across functions based on forecast.
        
        Args:
            forecast_df: Forecast DataFrame with forecast_workers_needed
            workers_available: Number of workers available
            
        Returns:
            DataFrame with allocation details
        """
        allocation_results = []
        
        for _, row in forecast_df.iterrows():
            workers_needed = row['forecast_workers_needed']
            
            # Calculate allocation
            allocation = {
                'date': row['date'],
                'workers_needed': workers_needed,
                'workers_available': workers_available,
                'workers_picking': int(workers_needed * self.ratios['picking']),
                'workers_packing': int(workers_needed * self.ratios['packing']),
                'workers_receiving': int(workers_needed * self.ratios['receiving']),
                'overtime_risk': workers_needed > workers_available,
                'shortage': max(0, workers_needed - workers_available)
            }
            
            allocation_results.append(allocation)
        
        return pd.DataFrame(allocation_results)

