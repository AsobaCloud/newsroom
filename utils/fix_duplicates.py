#!/usr/bin/env python3
"""
Fix duplicate cards in index.html
"""
import boto3
import re
from bs4 import BeautifulSoup

def fix_duplicate_cards():
    """Remove duplicate cards from index.html"""
    s3 = boto3.client('s3')
    bucket_name = 'news-collection-website'
    
    # Download current index.html
    response = s3.get_object(Bucket=bucket_name, Key='index.html')
    html_content = response['Body'].read().decode('utf-8')
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all news cards
    news_cards = soup.find_all('article', {'data-type': 'news'})
    
    # Group cards by date
    cards_by_date = {}
    for card in news_cards:
        title = card.find('h3', class_='card-title')
        if title:
            # Extract date from title like "Daily News Collection - 2025-10-19"
            match = re.search(r'Daily News Collection - (\d{4}-\d{2}-\d{2})', title.get_text())
            if match:
                date = match.group(1)
                if date not in cards_by_date:
                    cards_by_date[date] = []
                cards_by_date[date].append(card)
    
    # Remove duplicates (keep only the first card for each date)
    content_grid = soup.find('main', class_='content-grid')
    if content_grid:
        # Clear all cards
        for card in news_cards:
            card.decompose()
        
        # Add back only the first card for each date
        for date in sorted(cards_by_date.keys(), reverse=True):  # Most recent first
            first_card = cards_by_date[date][0]
            content_grid.append(first_card)
            print(f"Kept 1 card for {date} (removed {len(cards_by_date[date]) - 1} duplicates)")
    
    # Upload fixed HTML
    try:
        fixed_html = str(soup)
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=fixed_html.encode('utf-8'),
            ContentType='text/html'
        )
        print("Successfully uploaded fixed HTML to S3")
    except Exception as e:
        print(f"Error uploading: {e}")
        # Fallback: use original HTML but with manual duplicate removal
        print("Using fallback method...")
        # This is a simpler approach - just remove duplicate lines
        lines = html_content.split('\n')
        seen_dates = set()
        filtered_lines = []
        
        for line in lines:
            if 'Daily News Collection -' in line:
                # Extract date from this line
                match = re.search(r'Daily News Collection - (\d{4}-\d{2}-\d{2})', line)
                if match:
                    date = match.group(1)
                    if date not in seen_dates:
                        seen_dates.add(date)
                        # Include this card and the next few lines
                        card_start = lines.index(line)
                        # Find the end of this card (next </article>)
                        for i in range(card_start, len(lines)):
                            filtered_lines.append(lines[i])
                            if '</article>' in lines[i]:
                                break
                    else:
                        # Skip this duplicate card
                        card_start = lines.index(line)
                        for i in range(card_start, len(lines)):
                            if '</article>' in lines[i]:
                                break
                        continue
                else:
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)
        
        fixed_html = '\n'.join(filtered_lines)
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=fixed_html.encode('utf-8'),
            ContentType='text/html'
        )
        print("Successfully uploaded fixed HTML using fallback method")
    
    print("Fixed duplicate cards and uploaded to S3")

if __name__ == "__main__":
    fix_duplicate_cards()