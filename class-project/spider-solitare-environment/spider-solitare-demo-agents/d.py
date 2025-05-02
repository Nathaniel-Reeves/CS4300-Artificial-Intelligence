
import pandas as pd

def main():
    
    # Load pickle file "results.pkl"
    df = pd.read_pickle('./results.pkl')
    
    # filter out zeros from the num_completed_suits column
    df = df[df['num_completed_suits'] > 3]
    
    print(df)
    
    # Seeds 180, 223, 328, 566

if __name__ == '__main__':
    # This is the main function that is called when the script is run
    main()