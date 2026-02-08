import os
import logging
import gather_data
import process_data
import audit_quality

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    logging.info("Starting Clinical Data Pipeline...")
    
    logging.info("Step 1: Gathering Data")
    gather_data.main()
    
    logging.info("Step 2: Processing Data")
    process_data.main()
    
    logging.info("Step 3: Auditing Quality")
    audit_quality.main()
    
    logging.info("Pipeline Complete!")

if __name__ == "__main__":
    main()
