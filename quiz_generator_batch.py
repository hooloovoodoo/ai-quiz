#!/usr/bin/env python3
"""
Batch Quiz Generation Script

Generates multiple quiz variants for specified language(s) and saves them to /tmp directory.
Supports both English (ENG) and Serbian (SRB) languages with the new file structure.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from quiz_generator import QuizConfig, QuestionGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_quiz_variants(language: str = "ENG", num_variants: int = 10, output_dir: str = "/tmp") -> list:
    """
    Generate multiple quiz variants for the specified language
    
    Args:
        language: Language code ("ENG" or "SRB")
        num_variants: Number of quiz variants to generate
        output_dir: Directory to save generated quiz files
        
    Returns:
        List of generated file paths
    """
    
    logger.info(f"🎯 Generating {num_variants} quiz variants in {language}")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get current date for file naming
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create quiz configuration
    config = QuizConfig(
        title="AI Fundamentals",
        description="Test your knowledge across AI fundamentals, ethics, and practical applications",
        question_count=33,  # Total: 10 + 13 + 10
        points_per_question=5,
        language=language
    )
    
    # Initialize generator
    generator = QuestionGenerator(config)
    
    generated_files = []
    
    for variant_num in range(1, num_variants + 1):
        try:
            # Generate output filename with date and variant number
            filename = f"AI Fundamentals | {current_date} | [{language}] | Variant {variant_num}.gs"
            output_path = os.path.join(output_dir, filename)
            
            logger.info(f"📝 Generating variant {variant_num}/{num_variants}: {filename}")
            
            # Generate quiz for the specified language
            script_content = generator.generate_quiz_for_language(
                language=language,
                output_path=output_path,
                variant_number=variant_num
            )
            
            generated_files.append(output_path)
            logger.info(f"✅ Generated variant {variant_num}: {len(script_content)} characters")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate variant {variant_num}: {e}")
            continue
    
    logger.info(f"🎉 Successfully generated {len(generated_files)}/{num_variants} quiz variants")
    return generated_files


def list_generated_files(output_dir: str = "/tmp", language: str = None):
    """
    List all generated quiz files in the output directory
    
    Args:
        output_dir: Directory to search for quiz files
        language: Optional language filter ("ENG" or "SRB")
    """
    
    pattern = "AI Fundamentals | * | *.gs"
    if language:
        pattern = f"AI Fundamentals | * | [{language.upper()}] | *.gs"
    
    quiz_files = list(Path(output_dir).glob(pattern))
    
    if quiz_files:
        logger.info(f"📁 Found {len(quiz_files)} quiz files in {output_dir}:")
        for file_path in sorted(quiz_files):
            file_size = file_path.stat().st_size
            logger.info(f"   📄 {file_path.name} ({file_size:,} bytes)")
    else:
        logger.info(f"📁 No quiz files found in {output_dir}")
    
    return quiz_files


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate multiple quiz variants')
    
    parser.add_argument(
        '--language', '-l',
        choices=['ENG', 'SRB', 'BOTH'],
        default='ENG',
        help='Language for quiz generation (default: ENG)'
    )
    
    parser.add_argument(
        '--variants', '-n',
        type=int,
        default=10,
        help='Number of quiz variants to generate (default: 10)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='/tmp',
        help='Output directory for generated files (default: /tmp)'
    )
    
    parser.add_argument(
        '--list-files', '-ls',
        action='store_true',
        help='List existing quiz files in output directory'
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
        list_generated_files(args.output_dir, args.language if args.language != 'BOTH' else None)
        return 0
    
    # Validate arguments
    if args.variants <= 0:
        logger.error("❌ Number of variants must be positive")
        return 1
    
    try:
        all_generated_files = []
        
        if args.language == 'BOTH':
            # Generate for both languages
            logger.info("🌐 Generating quizzes for both languages")
            
            # Generate English variants
            eng_files = generate_quiz_variants('ENG', args.variants, args.output_dir)
            all_generated_files.extend(eng_files)
            
            # Generate Serbian variants
            srb_files = generate_quiz_variants('SRB', args.variants, args.output_dir)
            all_generated_files.extend(srb_files)
            
        else:
            # Generate for single language
            generated_files = generate_quiz_variants(args.language, args.variants, args.output_dir)
            all_generated_files.extend(generated_files)
        
        # Summary
        if all_generated_files:
            logger.info(f"🎊 Generation complete! Created {len(all_generated_files)} quiz files")
            logger.info(f"📂 Files saved to: {args.output_dir}")
            
            # List generated files
            list_generated_files(args.output_dir)
            
            return 0
        else:
            logger.error("❌ No quiz files were generated")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⏹️  Generation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
