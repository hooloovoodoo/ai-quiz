#!/usr/bin/env python3
"""
Batch Quiz Deployment Script

Deploys all generated quiz variants from /tmp to Google Apps Script
"""

import argparse
import logging
import glob
from pathlib import Path
from gas_deployer import GoogleAppsScriptDeployer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def deploy_all_quizzes(pattern: str = "/tmp/AI Fundamentals | * | Variant *.gs", language: str = None):
    """
    Deploy all quiz variants from /tmp directory
    
    Args:
        pattern: Glob pattern to find quiz files
        language: Optional language filter ("ENG", "SRB", or None for all)
        
    Returns:
        List of deployed quiz information
    """
    
    # Find matching files
    quiz_files = glob.glob(pattern)
    
    # Filter by language if specified
    if language:
        language = language.upper()
        quiz_files = [f for f in quiz_files if f"[{language}]" in f]
        logger.info(f"🚀 Starting batch quiz deployment for {language} quizzes...")
        if not quiz_files:
            logger.warning(f"⚠️  No {language} quiz files found")
            return []
    else:
        logger.info("🚀 Starting batch quiz deployment for all languages...")
    
    if not quiz_files:
        logger.warning(f"⚠️  No quiz files found matching pattern: {pattern}")
        return []
    
    logger.info(f"📄 Found {len(quiz_files)} quiz files to deploy")
    
    # Initialize deployer
    deployer = GoogleAppsScriptDeployer()
    
    # Authenticate
    if not deployer.authenticate_google():
        logger.error("❌ Authentication failed")
        return []
    
    # Deploy all quizzes
    deployed_quizzes = deployer.deploy_batch_quiz_scripts(pattern)
    
    if deployed_quizzes:
        logger.info(f"🎉 Successfully deployed {len(deployed_quizzes)} quiz variants!")
        
        # Export URLs to a file for easy access
        if language:
            urls_file = f"/tmp/quiz_urls_{language.lower()}.txt"
            file_header = f"Deployed {language} Quiz URLs:"
        else:
            urls_file = "/tmp/quiz_urls_all.txt"
            file_header = "Deployed Quiz URLs (All Languages):"
            
        with open(urls_file, 'w') as f:
            f.write(f"{file_header}\n")
            f.write("=" * len(file_header) + "\n")
            
            # Group by language for better organization
            eng_quizzes = [q for q in deployed_quizzes if '[ENG]' in q.get('name', '')]
            srb_quizzes = [q for q in deployed_quizzes if '[SRB]' in q.get('name', '')]
            
            if eng_quizzes:
                f.write("\n🇺🇸 ENGLISH QUIZZES:\n")
                f.write("-" * 20 + "\n")
                for quiz in eng_quizzes:
                    f.write(f"Variant {quiz['variant']}: {quiz['edit_url']}\n")
            
            if srb_quizzes:
                f.write("\n🇷🇸 SERBIAN QUIZZES:\n")
                f.write("-" * 20 + "\n")
                for quiz in srb_quizzes:
                    f.write(f"Variant {quiz['variant']}: {quiz['edit_url']}\n")
            
            # If no language info available, fall back to simple list
            if not eng_quizzes and not srb_quizzes:
                for quiz in deployed_quizzes:
                    f.write(f"Variant {quiz['variant']}: {quiz['edit_url']}\n")
        
        logger.info(f"📄 URLs saved to: {urls_file}")
        
    return deployed_quizzes


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Deploy all generated quiz variants')
    
    parser.add_argument(
        '--pattern', 
        default="/tmp/AI Fundamentals | * | Variant *.gs",
        help='Glob pattern to find quiz files (default: matches new naming format)'
    )
    
    parser.add_argument(
        '--language', '-l',
        choices=['ENG', 'SRB'],
        help='Deploy only quizzes for specific language (ENG or SRB)'
    )
    
    parser.add_argument(
        '--list-files', '-ls',
        action='store_true',
        help='List available quiz files without deploying'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # List files if requested
    if args.list_files:
        quiz_files = glob.glob(args.pattern)
        
        # Filter by language if specified
        if args.language:
            quiz_files = [f for f in quiz_files if f"[{args.language}]" in f]
        
        if quiz_files:
            lang_msg = f" ({args.language} only)" if args.language else ""
            logger.info(f"📁 Found {len(quiz_files)} quiz files{lang_msg}:")
            for file_path in sorted(quiz_files):
                file_name = Path(file_path).name
                file_size = Path(file_path).stat().st_size
                logger.info(f"   📄 {file_name} ({file_size:,} bytes)")
        else:
            lang_msg = f" for {args.language}" if args.language else ""
            logger.info(f"📁 No quiz files found{lang_msg}")
        return 0
    
    # Deploy quizzes
    deployed_quizzes = deploy_all_quizzes(args.pattern, args.language)
    
    if deployed_quizzes:
        print("\n🔗 Quick Access URLs:")
        
        # Group by language for better display
        eng_quizzes = [q for q in deployed_quizzes if '[ENG]' in q.get('name', '')]
        srb_quizzes = [q for q in deployed_quizzes if '[SRB]' in q.get('name', '')]
        
        if eng_quizzes:
            print("   🇺🇸 English Quizzes:")
            for quiz in eng_quizzes:
                print(f"      Variant {quiz['variant']}: {quiz['edit_url']}")
        
        if srb_quizzes:
            print("   🇷🇸 Serbian Quizzes:")
            for quiz in srb_quizzes:
                print(f"      Variant {quiz['variant']}: {quiz['edit_url']}")
        
        # If no language info available, fall back to simple list
        if not eng_quizzes and not srb_quizzes:
            for quiz in deployed_quizzes:
                print(f"   Variant {quiz['variant']}: {quiz['edit_url']}")
        
        return 0
    else:
        logger.error("❌ No quizzes were deployed")
        return 1


if __name__ == "__main__":
    exit(main())
