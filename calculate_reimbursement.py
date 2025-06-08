import sys
import random

# Federal guideline-inspired lookup table
PER_DIEM_TABLE = {
    "Low": {"BaseRate": 15, "MieRate": 5},  # e.g., Detroit, low-effort
    "Medium": {"BaseRate": 50, "MieRate": 15},  # CONUS
    "High": {"BaseRate": 65, "MieRate": 20}  # e.g., New York, high-effort
}

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, use_system_date=False, add_noise=False):
    """
    Calculate reimbursement using a fitted model with effort-based adjustments.
    Args:
        trip_duration_days (int): Number of days (1-14).
        miles_traveled (float): Miles traveled (6-1317.07).
        total_receipts_amount (float): Total receipts ($1.42-$2494.69).
        use_system_date (bool): If True, use system date; if False, use fixed rate.
        add_noise (bool): If True, add 5-10% noise; if False, deterministic output.
    Returns:
        float: Reimbursement amount, rounded to 2 decimal places.
    """
    # Step 1: Calculate efficiency
    efficiency = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0

    # Step 2: Infer location based on effort
    if efficiency > 200 or (miles_traveled > 800 and total_receipts_amount > 1000):
        location = "High"  # High-effort or high activity
    elif efficiency < 50 or (trip_duration_days > 7 and efficiency < 100):
        location = "Low"  # Low-effort or coasting
    else:
        location = "Medium"  # Moderate effort

    base_rate = PER_DIEM_TABLE[location]["BaseRate"]
    m_and_ie_rate = PER_DIEM_TABLE[location]["MieRate"]
    cycle_factor = 1.0

    # Step 3: Calculate per diem
    if trip_duration_days >= 2:
        per_diem = (base_rate + m_and_ie_rate) * (trip_duration_days - 2) + \
                   (base_rate + m_and_ie_rate * 0.75) * 2
    else:
        per_diem = (base_rate + m_and_ie_rate) * trip_duration_days

    duration_factor = 1.0
    if trip_duration_days == 5:
        duration_factor = 1.15  # 5-day bonus
    elif trip_duration_days > 7:
        duration_factor = 0.40 if location == "Low" else 0.80  # Strong penalty for Low-effort

    per_diem *= duration_factor

    # Step 4: Calculate mileage
    mileage_reimbursement = 0.0
    if miles_traveled >= 50:
        if miles_traveled <= 100:
            mileage_reimbursement = miles_traveled * 0.70
        elif miles_traveled <= 500:
            mileage_reimbursement = (100 * 0.70) + ((miles_traveled - 100) * 0.60)
        else:
            mileage_reimbursement = (100 * 0.70) + (400 * 0.60) + ((miles_traveled - 500) * 0.50)

    efficiency_factor = 1.0
    if efficiency > 200:
        efficiency_factor = 1.20  # Reward high effort
    elif efficiency > 100 and efficiency <= 200:
        efficiency_factor = 1.15
    elif efficiency > 300 and trip_duration_days > 1:
        efficiency_factor = 0.90

    mileage_reimbursement *= efficiency_factor

    # Step 5: Calculate receipts
    receipt_adjustment = 0.0
    if total_receipts_amount < 50:
        receipt_adjustment = per_diem
    elif total_receipts_amount <= 500 and trip_duration_days <= 6:
        receipt_adjustment = min(per_diem * 0.8, total_receipts_amount)
    else:
        excess = min(total_receipts_amount - per_diem, 200 if efficiency < 100 else 500)
        receipt_adjustment = per_diem + excess * 0.15

    # Step 6: Apply cyclical suppression for low-effort
    if location == "Low" and efficiency < 100:
        cycle_factor *= 0.85

    # Step 7: Combine components
    reimbursement = per_diem + mileage_reimbursement + receipt_adjustment
    reimbursement *= cycle_factor

    # Step 8: Cap for low-effort trips
    if efficiency < 50:
        reimbursement = min(reimbursement, trip_duration_days * 100)  # Cap at $100/day

    # Step 9: Apply random noise (if enabled)
    if add_noise:
        noise_factor = 0.95 + (random.random() * 0.10)
        reimbursement *= noise_factor

    # Step 10: Round to two decimal places
    reimbursement = round(reimbursement, 2)

    return reimbursement

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>", file=sys.stderr)
        sys.exit(1)

    try:
        trip_duration_days = int(sys.argv[1])
        miles_traveled = float(sys.argv[2])
        total_receipts_amount = float(sys.argv[3])
        result = calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, use_system_date=False, add_noise=False)
        print(result)
    except ValueError as e:
        print(f"Error: Invalid input format ({e})", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
